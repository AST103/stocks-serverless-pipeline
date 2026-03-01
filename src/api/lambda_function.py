# create lambda function that reads from the dynamo db and returns last 7 days of winning stocks
from decimal import Decimal
import json
import os
import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLE_NAME", "stock-winners")
# to instantiate a DynamoDB resource
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):

    try:
        # scan the table
        response = table.scan() # note: for larger tables this can be optimized since we are scanning entire table
        items = response.get("Items", [])

        # sort items by date in descending order and get the last 7 days
        sorted_items = sorted(
            items, key=lambda x: x["date"], reverse=True
        )  # default is ascending
        last_7_days = sorted_items[:7]  # get the last 7 items

        #API gateway expects body to be a string

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  # Allow CORS for all origins
                "Access-Control-Allow-Methods": "GET, OPTIONS",  # Allow only GET requests
                "Access-Control-Allow-Headers": "Content-Type",  # Allow only Content-Type header
            },
            "body": json.dumps(last_7_days, default=decimal_to_float), # convert for dynamodb 
        }

    except ClientError as e:
        print(f"Error fetching data from DynamoDB: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  # Allow CORS for all origins
            },
            "body": json.dumps({"error": "Error fetching data from DynamoDB"}),
        }

    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  # Allow CORS for all origins
            },
            "body": json.dumps({"error": "Unexpected error occurred"}),
        }
