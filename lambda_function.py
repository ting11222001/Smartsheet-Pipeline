import json
import logging 

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context): # event contains the incoming request data
    logger.info("Received event: %s", json.dumps(event))
    
    # Process the event here
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

    logger.info("Processing row %s with status %s", row_id, status)

    return {
        "statusCode": 200,
        "body": json.dumps({ # json.dumps converts the Python dictionary back into a string, because API Gateway expects the body to be a string.
            "message": "Row processed successfully",
            "row_id": row_id,
            "status": status,
            "project_name": project_name
        })
    }