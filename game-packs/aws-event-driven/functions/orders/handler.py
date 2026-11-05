import json
import os
import uuid
from datetime import datetime, timezone

import boto3

ENDPOINT = os.getenv("AWS_ENDPOINT_URL")
REGION = os.getenv("AWS_REGION", "us-east-1")
ORDERS_TABLE = os.getenv("ORDERS_TABLE", "arena-orders")
EVENT_BUS = os.getenv("EVENT_BUS_NAME", "orders-bus")


def client(service):
    kwargs = {"region_name": REGION}
    if ENDPOINT:
        kwargs.update(endpoint_url=ENDPOINT, aws_access_key_id="test", aws_secret_access_key="test")
    return boto3.client(service, **kwargs)


def handler(event, context):
    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        import base64
        body = base64.b64decode(body).decode("utf-8")
    payload = json.loads(body) if isinstance(body, str) else body
    order_id = payload.get("orderId") or str(uuid.uuid4())
    order = {
        "orderId": order_id,
        "customerId": str(payload.get("customerId", "demo-customer")),
        "total": str(payload.get("total", "100.00")),
        "status": "CREATED",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    client("dynamodb").put_item(TableName=ORDERS_TABLE, Item={
        "orderId": {"S": order["orderId"]},
        "customerId": {"S": order["customerId"]},
        "total": {"N": order["total"]},
        "status": {"S": order["status"]},
        "createdAt": {"S": order["createdAt"]},
    })
    event_detail = {"orderId": order_id, "customerId": order["customerId"], "total": order["total"]}
    publish_result = client("events").put_events(Entries=[{
        "EventBusName": EVENT_BUS,
        "Source": "com.cloudopsarena.orders",
        "DetailType": "OrderCreated",
        "Detail": json.dumps(event_detail),
    }])
    if publish_result.get("FailedEntryCount", 0):
        raise RuntimeError(f"EventBridge failed to publish OrderCreated: {publish_result.get('Entries')}")
    return {"statusCode": 201, "headers": {"content-type": "application/json"}, "body": json.dumps(order)}
