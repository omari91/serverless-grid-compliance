import json
import boto3
import os
import logging
import pandapower as pp
# Explicitly import simplejson for better decimal handling if available, else standard
from decimal import Decimal

# --- CONFIGURATION ---
DYNAMODB_TABLE = 'GridComplianceResults'
VOLTAGE_MIN_PU = 0.90
VOLTAGE_MAX_PU = 1.10

# Initialize Clients (Outside Handler for Warm Start)
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    AWS Lambda Entrypoint: Validates VDE-AR-N 4110 compliance.
    """
    logger.info("⚡ Starting Grid Compliance Check...")
    
    try:
        # 1. Parse Event
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']  # e.g., "scenarios/berlin_grid.json"
        
        logger.info(f"Processing File: {file_key} from {bucket_name}")

        # 2. Secure File Download (Fixing the Folder Crash)
        # /tmp is the only writable directory in Lambda
        download_path = f"/tmp/{os.path.basename(file_key)}"
        
        s3.download_file(bucket_name, file_key, download_path)
        
        # 3. Load & Run Physics
        try:
            net = pp.from_json(download_path)
            logger.info(f"Network Loaded: {len(net.bus)} buses")
            
            # Run Newton-Raphson
            pp.runpp(net, algorithm='nr')
        except pp.LoadflowNotConverged:
            logger.error("⚠️ Power Flow Divergence")
            return _log_result(file_key, "ERROR", "Divergence", [])
        except Exception as e:
            logger.error(f"❌ Pandapower Error: {e}")
            raise e

        # 4. Compliance Logic (VDE-AR-N 4110)
        violations = []
        for bus_idx, row in net.res_bus.iterrows():
            vm_pu = row['vm_pu']
            
            # Check Limits
            if vm_pu < VOLTAGE_MIN_PU or vm_pu > VOLTAGE_MAX_PU:
                violations.append({
                    'bus_id': int(bus_idx),  # Cast Numpy int -> Python int
                    'voltage_pu': Decimal(str(round(vm_pu, 4))), # Float -> Decimal for DynamoDB
                    'type': 'Undervoltage' if vm_pu < VOLTAGE_MIN_PU else 'Overvoltage'
                })

        status = "FAIL" if violations else "PASS"
        logger.info(f"Compliance Result: {status} ({len(violations)} violations)")

        # 5. Persist to DynamoDB
        _log_result(file_key, status, "VDE-AR-N 4110", violations)

        return {
            'statusCode': 200, 
            'body': json.dumps({'status': status, 'file': file_key})
        }

    except Exception as e:
        logger.error(f"🔥 Critical Failure: {str(e)}")
        # Re-raising ensures S3 retries or sends to Dead Letter Queue
        raise e

def _log_result(file_key, status, standard, violations):
    """Helper to write to DynamoDB with correct Types"""
    from datetime import datetime
    
    table = dynamodb.Table(DYNAMODB_TABLE)
    table.put_item(Item={
        'grid_id': file_key,
        'timestamp': datetime.now().isoformat(),
        'status': status,
        'compliance_standard': standard,
        'violations': violations, # DynamoDB accepts List[Map]
        'processed_by': 'AWS_Lambda'
    })
