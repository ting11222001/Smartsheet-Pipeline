import json
import logging
import os
import csv
import io
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON"})
        }

    row_id = body.get("row_id")
    status = body.get("status")
    project_name = body.get("project_name")

    if not all([row_id, status, project_name]):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required fields: row_id, status, project_name"})
        }

    # Write to DynamoDB
    table_name = os.environ["DYNAMODB_TABLE"]
    table = dynamodb.Table(table_name)
    table.put_item(Item={  # put_item is the method to write data to DynamoDB
        "row_id": row_id,
        "status": status,
        "project_name": project_name
    })
    logger.info("Saved row %s to DynamoDB", row_id)

    # Write to S3 if status is Complete
    if status == "Complete":
        bucket_name = os.environ["S3_BUCKET"]
        csv_buffer = io.StringIO()              # Lambda doesn't have a filesystem, so use an in-memory buffer. It behaves like a file, but lives in RAM.
        writer = csv.writer(csv_buffer)         # formats data as CSV
        writer.writerow(["row_id", "status", "project_name"])
        writer.writerow([row_id, status, project_name])

        s3.put_object(
            Bucket=bucket_name,
            Key=f"summaries/{row_id}.csv",
            Body=csv_buffer.getvalue()          # "row_id,status,project_name\r\n101,Complete,Bridge Construction\r\n" 
        )
        logger.info("Wrote CSV to S3 for row %s", row_id)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Row processed successfully",
            "row_id": row_id,
            "status": status,
            "project_name": project_name
        })
    }