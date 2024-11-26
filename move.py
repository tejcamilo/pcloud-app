import json
import boto3
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the DynamoDB resource with session token
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

dynamodb = session.resource('dynamodb')

# Load the data from patients.json
with open('patients.json') as f:
    patients = json.load(f)

# Specify the table name
table_name = 'patients'
table = dynamodb.Table(table_name)

# Batch write the data to DynamoDB
with table.batch_writer() as batch:
    for patient in patients:
        # Flatten the _id field
        if '_id' in patient and '$oid' in patient['_id']:
            patient['_id'] = patient['_id']['$oid']
        else:
            print(f"Skipping patient without valid _id: {patient}")
            continue
        batch.put_item(Item=patient)

print("Data uploaded successfully.")