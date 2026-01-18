# Contributing to Serverless Grid Compliance

Thank you for your interest in contributing to the Serverless Grid Compliance Pipeline! This project automates VDE-AR-N 4110 voltage stability validation using AWS Lambda and Pandapower. We welcome contributions from power systems engineers, cloud architects, and developers.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Guidelines](#development-guidelines)
- [AWS Lambda Specific Guidelines](#aws-lambda-specific-guidelines)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a welcoming and inclusive environment. Be respectful, collaborative, and constructive in all interactions.

## Getting Started

### Prerequisites

- **Python 3.9+**
- **AWS Account** with Lambda, S3, and DynamoDB access
- **AWS CLI** configured with appropriate credentials
- **Boto3** (AWS SDK for Python)
- **Pandapower** knowledge (helpful but optional)
- Understanding of **power systems** and **VDE-AR-N 4110** standards

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/serverless-grid-compliance.git
   cd serverless-grid-compliance
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up AWS credentials** (if testing AWS integrations locally)
   ```bash
   aws configure
   ```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When reporting:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected vs. actual results**
- **AWS Lambda logs** or error traces (sanitize sensitive data)
- **Grid data format** used (if applicable)
- **Python version** and dependency versions

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Include:

- **Use case description** - What DSO/TSO problem does this solve?
- **Proposed solution** - How should it work?
- **Alternatives considered**
- **Impact on Lambda performance** - Cold start, execution time, memory usage
- **Relevance to grid standards** (VDE-AR-N 4110, VDE-AR-N 4120, IEC standards)

### Areas Where Contributions Are Welcome

1. **Grid Compliance Extensions**
   - Additional VDE-AR-N standards (4105, 4120)
   - Line loading (thermal limit) checks
   - IEC 61850 integration
   - CGMES (CIM) data format support

2. **AWS Infrastructure**
   - CloudFormation/Terraform templates for deployment
   - Step Functions for orchestration
   - EventBridge integration for real-time processing
   - API Gateway for REST endpoints

3. **Performance Optimization**
   - Lambda cold start reduction
   - Parallel processing with Lambda concurrency
   - S3 caching strategies
   - Memory vs. execution time trade-offs

4. **Grid Modeling**
   - Additional Pandapower features
   - Newton-Raphson solver optimizations
   - Three-phase unbalanced load flow
   - Dynamic simulation capabilities

5. **Documentation**
   - AWS deployment guides
   - Grid modeling examples
   - API documentation
   - Redispatch 3.0 use cases

## Development Guidelines

### Branch Naming Convention

Use descriptive branch names:

- `feature/description` - New features (e.g., `feature/vde-4120-support`)
- `fix/description` - Bug fixes (e.g., `fix/lambda-timeout-issue`)
- `docs/description` - Documentation updates
- `infra/description` - Infrastructure changes
- `test/description` - Test additions

### Commit Messages

Write clear, concise commit messages:

```
Add VDE-AR-N 4120 line loading checks

- Implement thermal limit validation
- Add S3 event trigger for real-time processing
- Update Lambda memory to 512MB for larger grids

Addresses #15
```

Format:
- Imperative mood ("Add" not "Added")
- First line: Brief summary (50 characters or less)
- Blank line
- Detailed description
- Reference related issues

## AWS Lambda Specific Guidelines

### Lambda Function Structure

Keep Lambda functions:
- **Stateless** - No local state persistence
- **Single responsibility** - One function per task
- **Idempotent** - Same input produces same output
- **Error-handled** - Graceful degradation with retries

### Performance Best Practices

1. **Cold Start Optimization**
   - Import modules globally, not inside handler
   - Use Lambda layers for large dependencies
   - Consider Provisioned Concurrency for critical paths

2. **Memory Configuration**
   - Test different memory allocations (128MB - 3008MB)
   - More memory = more CPU power
   - Monitor CloudWatch metrics for optimization

3. **Execution Time**
   - Keep under 15 minutes (Lambda max)
   - Break large grids into batches
   - Use Step Functions for long-running workflows

### Code Example

```python
import json
import boto3
import pandapower as pp
import logging

# Global initialization (outside handler)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    \"\"\"
    AWS Lambda handler for grid compliance validation.
    
    Args:
        event: S3 event trigger with grid model reference
        context: Lambda execution context
        
    Returns:
        dict: Compliance results with voltage violations
    \"\"\"
    try:
        # Extract S3 bucket and key from event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        # Load grid model from S3
        grid_data = load_grid_from_s3(bucket, key)
        
        # Run power flow simulation
        results = run_compliance_check(grid_data)
        
        # Store results in DynamoDB
        store_results(results)
        
        return {
            'statusCode': 200,
            'body': json.dumps(results)
        }
        
    except Exception as e:
        logger.error(f\"Compliance check failed: {str(e)}\")
        raise
```

### Environment Variables

Use Lambda environment variables for configuration:

- `VOLTAGE_TOLERANCE` - Voltage deviation threshold (default: 0.10)
- `DYNAMODB_TABLE` - Results table name
- `LOG_LEVEL` - Logging verbosity (INFO, DEBUG, ERROR)

## Testing

### Local Testing

Test Lambda function locally before deployment:

```bash
# Test with sample grid data
python lambda_function.py

# Use AWS SAM for local Lambda simulation
sam local invoke GridComplianceFunction -e test_events/sample_grid.json
```

### Unit Tests

Write unit tests for grid logic:

```python
def test_voltage_compliance_check():
    \"\"\"Test voltage compliance against VDE-AR-N 4110.\"\"\"
    # Arrange
    grid = create_test_grid()
    
    # Act
    results = check_voltage_compliance(grid)
    
    # Assert
    assert results['compliant'] == False
    assert results['violations'] > 0
    assert 0.90 <= results['min_voltage'] <= 1.10
```

### Integration Tests

Test AWS integrations:
- S3 event triggers
- DynamoDB writes
- Lambda invocations

Use **LocalStack** or **moto** for AWS service mocking.

## Pull Request Process

### Before Submitting

1. **Update your branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run tests** and ensure they pass

3. **Update documentation** if changing functionality

4. **Check Lambda size** - Keep deployment package under 50MB (unzipped)

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Lambda function tested locally
- [ ] No hardcoded AWS credentials
- [ ] Environment variables documented
- [ ] CloudWatch logs reviewed
- [ ] Memory and timeout configured appropriately
- [ ] Error handling implemented
- [ ] Commit messages are clear
- [ ] No merge conflicts

### PR Review Process

- Maintainers will review within 3-5 business days
- Address feedback by pushing new commits
- Once approved, PR will be merged
- Delete your branch after merge

## Additional Resources

### Power Systems Standards

- [VDE-AR-N 4110](https://www.vde.com/en/fnn/topics/technical-connection-rules) - Medium voltage grid connection
- [VDE-AR-N 4120](https://www.vde.com/en/fnn) - High voltage grid connection
- [Redispatch 3.0](https://www.bundesnetzagentur.de/EN/Areas/Energy/Companies/GridMatters/Redispatch/start.html) - German grid dispatch reform

### AWS Resources

- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Pandapower Documentation](https://pandapower.readthedocs.io/)
- [Boto3 SDK Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

### Development Tools

- **AWS SAM** - Serverless application testing
- **LocalStack** - Local AWS service emulation
- **Pylint** - Python linting
- **Black** - Code formatting (optional)

---

**Thank you for contributing to grid digitalization and Redispatch 3.0 automation!**

For questions, open a discussion or reach out through GitHub issues.
