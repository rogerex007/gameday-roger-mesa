import json
import os

import boto3
from botocore.exceptions import ClientError

ENDPOINT = os.getenv("AWS_ENDPOINT_URL")
REGION = os.getenv("AWS_REGION", "us-east-1")
IDEMPOTENCY_TABLE = os.getenv("IDEMPOTENCY_TABLE", "arena-idempotency")
FAIL_PAYMENTS = os.getenv("FAIL_PAYMENTS", "false").lower() == "true"


def dynamodb():
    kwargs = {"region_name": REGION}
    if ENDPOINT:
        kwargs.update(endpoint_url=ENDPOINT, aws_access_key_id="test", aws_secret_access_key="test")
    return boto3.client("dynamodb", **kwargs)


def handler(event, context):
    if FAIL_PAYMENTS:
        raise RuntimeError("Injected GameDay incident: payment processor unavailable")
    failures = []
    for record in event.get("Records", []):
        try:
            envelope = json.loads(record["body"])
            detail = envelope.get("detail", envelope)
            order_id = str(detail["orderId"])
            event_id = order_id  # Idempotency is per business operation, not per delivery attempt.
            dynamodb().put_item(
                TableName=IDEMPOTENCY_TABLE,
                Item={"eventId": {"S": event_id}, "service": {"S": "payments"}, "orderId": {"S": order_id}},
                ConditionExpression="attribute_not_exists(eventId)",
            )
            print(json.dumps({"level": "INFO", "message": "payment simulated", "orderId": order_id, "eventId": event_id}))
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                print(json.dumps({"level": "INFO", "message": "duplicate event ignored", "recordId": record["messageId"]}))
                continue
            failures.append({"itemIdentifier": record["messageId"]})
        except Exception as exc:
            print(json.dumps({"level": "ERROR", "message": str(exc), "recordId": record.get("messageId")}))
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures}
