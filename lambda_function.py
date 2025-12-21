import json
import boto3
import os
import pandapower as pp
import pandas as pd
from datetime import datetime

# Initialize AWS Clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

DYNAMODB_TABLE = 'GridComplianceResults'
VOLTAGE_MIN_PU = 0.90
VOLTAGE_MAX_PU = 1.10

def lambda_handler(event, context):
    print("Starting Grid Compliance Check...")
    try:
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']
        download_path = f'/tmp/{file_key}'
        
        s3.download_file(bucket_name, file_key, download_path)
        
        net = pp.from_json(download_path)
        pp.runpp(net)
        
        violations = []
        for bus_idx, row in net.res_bus.iterrows():
            vm_pu = row['vm_pu']
            if vm_pu < VOLTAGE_MIN_PU or vm_pu > VOLTAGE_MAX_PU:
                violations.append({
                    'bus_id': int(bus_idx),
                    'voltage_pu': float(round(vm_pu, 4)),
                    'type': 'Undervoltage' if vm_pu < VOLTAGE_MIN_PU else 'Overvoltage'
                })
        
        status = "FAIL" if violations else "PASS"

        table = dynamodb.Table(DYNAMODB_TABLE)
        table.put_item(Item={
            'grid_id': file_key,
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'violations': violations,
            'compliance_standard': 'VDE-AR-N 4110'
        })
        
        return {'statusCode': 200, 'body': json.dumps(f"Check Complete: {status}")}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise e