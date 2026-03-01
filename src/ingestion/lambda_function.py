# this is for our cron job
import os
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import boto3
import requests

# connect to the API
# iterate through the watchlist

TABLE_NAME = os.environ.get("TABLE_NAME", "stock-winners")
API_KEY = os.environ.get("MASSIVE_API_KEY")
WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"]

# to instantiate a DynamoDB resource
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):

    try:
        ### WE SHOULD ONLY NEED TO BACKFILL ONCE, CAN REMOVE THIS CHECK AFTER A WEEK OF DATA HAS BEEN COLLECTED ###
        # check if table has less than 7 items, if so we need to backfill data for the past week
        response = table.scan(Select="COUNT")
        item_count = response.get("Count", 0)

        if item_count < 7:
            print(
                f"Table has {item_count} items, backfilling data for the past week..."
            )

            current_count = item_count
            for i in range(1, 15):
                if current_count >= 7:
                    print("Table already has 7 or more items. Stopping backfill.")
                    break

                target_date_obj = datetime.now(timezone.utc) - timedelta(days=i)
                target_date = target_date_obj.strftime("%Y-%m-%d")

                if target_date_obj.date() >= datetime.now(timezone.utc).date():
                    print(f"{target_date} Skipping today.")
                    continue

                if target_date_obj.weekday() >= 5:  # Skip weekends
                    print(f"{target_date} is a weekend. Skipping.")
                    continue

                try:  # if already exists
                    check = table.get_item(
                        Key={
                            "date": target_date,
                        }
                    )
                    if "Item" in check:
                        print(f"Data for {target_date} already exists. Skipping fetch.")
                        current_count += (
                            1  # if it already exists we should still increment
                        )
                        continue

                except Exception as e:
                    print(f"Error checking for existing data on {target_date}: {e}")
                    continue

                winner = fetch_winner_on_date(target_date)
                if winner:
                    write_winner_to_dynamodb(winner)
                    current_count += 1
                else:
                    print(f"No winner found for {target_date}. Skipping.")
                time.sleep(15)  # Rate limit protection during backfill
        ####

        winner = fetch_winner()
        if winner:
            success = write_winner_to_dynamodb(winner)

            if success:
                return {
                    "statusCode": 200,
                    "body": f"The stock with the highest percent change today is: {winner['ticker']} with a change of {winner['percentChange']}%",
                }
            else:
                return {
                    "statusCode": 500,
                    "body": "Failed to write winner to DynamoDB.",
                }
        else:
            return {"statusCode": 500, "body": "No winner found."}

    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        return {"statusCode": 500, "body": f"An error occurred: {e}"}


# calculate which stock had highest percent change (absolute value) for the day
def fetch_winner():
    results = []

    for idx, stock in enumerate(WATCHLIST):
        try:
            url = f"https://api.massive.com/v2/aggs/ticker/{stock}/prev?adjusted=true&apiKey={API_KEY}"
            response = requests.get(
                url, timeout=10
            )  # set a timeout of 10 seconds for the request

            if response.status_code == 429:
                print(f"Rate limit exceeded for {stock}. waiting...")
                time.sleep(60)
                response = requests.get(
                    url, timeout=10
                )  # retry the request after waiting

            response.raise_for_status()  # raise an exception for HTTP errors

            data = response.json()

            # validate that data has the expected structure
            if not data.get("results"):
                print(f"No results found for {stock}. Skipping.")
                continue

            open_price = data["results"][0]["o"]
            close_price = data["results"][0]["c"]
            percent_change = (
                (close_price - open_price) / open_price
            ) * 100  # Keep sign for green/red coloring

            # timestamp t is in unix milliseconds, convert to date
            date = data["results"][0]["t"] / 1000  # div by 1000 to convert to seconds
            date_obj = datetime.fromtimestamp(
                date, tz=timezone.utc
            )  # convert to datetime object in UTC
            date_str = date_obj.strftime("%Y-%m-%d")  # format as YYYY-MM-DD

            stock_data = {
                "date": date_str,
                "ticker": stock,
                "percentChange": Decimal(str(round(percent_change, 2))),
                "closePrice": Decimal(str(round(close_price, 2))),
            }
            results.append(stock_data)

            if idx < len(WATCHLIST) - 1:
                time.sleep(12)  # Rate limit protection

        # Handles network errors, timeouts, and HTTP errors like 4xx and 5xx status codes
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {stock}: {e}")
            continue

        # Handles cases where the expected data structure is not present in the API response
        except (KeyError, ValueError, TypeError) as e:
            print(f"Unexpected data format for {stock}: {e}")
            continue

    if not results:
        print("No valid data fetched for any stock.")
        return None

    # find the stock with the highest percent change (by absolute value)
    winner = max(results, key=lambda x: abs(x["percentChange"]))
    return winner


# date MUST be passed in YYYY-MM-DD format
def fetch_winner_on_date(target_date):
    results = []

    for stock in WATCHLIST:
        try:
            url = f"https://api.massive.com/v1/open-close/{stock}/{target_date}?adjusted=true&apiKey={API_KEY}"
            response = requests.get(
                url=url, timeout=10
            )  # set a timeout of 10 seconds for the request

            if response.status_code == 429:
                print(f"Rate limit exceeded for {stock}. waiting...")
                time.sleep(60)
                response = requests.get(
                    url, timeout=10
                )  # retry the request after waiting

            response.raise_for_status()  # raise an exception for HTTP errors

            data = response.json()

            if not data.get("open") or not data.get("close"):
                print(
                    f"Missing open or close data for {stock} on {target_date}. Skipping."
                )
                continue

            date_str = data["from"]
            open_price = data["open"]
            close_price = data["close"]
            percent_change = (
                (close_price - open_price) / open_price
            ) * 100  # Keep sign for green/red coloring

            stock_data = {
                "date": date_str,
                "ticker": stock,
                "percentChange": Decimal(str(round(percent_change, 2))),
                "closePrice": Decimal(str(round(close_price, 2))),
            }
            results.append(stock_data)
            time.sleep(12)

        # Handles network errors, timeouts, and HTTP errors like 4xx and 5xx status codes
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {stock} on {target_date}: {e}")
            time.sleep(12)
            continue

        # Handles cases where the expected data structure is not present in the API response
        except (KeyError, ValueError, TypeError) as e:
            print(f"Unexpected data format for {stock} on {target_date}: {e}")
            continue

    if not results:
        print("No valid data fetched for any stock.")
        return None

    ## for debugging
    # print(f"Percent changes for {target_date}: {[{'ticker': r['ticker'], 'percentChange': r['percentChange']} for r in results]}")

    ##

    # find the stock with the highest percent change (by absolute value)
    winner = max(results, key=lambda x: abs(x["percentChange"]))

    return winner


# store result in DynamoDB
def write_winner_to_dynamodb(winner):

    # first check if it already exists
    try:
        response = table.get_item(
            Key={
                "date": winner["date"],
            }
        )
        # check if response contains an Item key, if so it means an item with that date already exists
        if "Item" in response:
            print(
                f"Winner for {winner['ticker']} on {winner['date']} already exists in DynamoDB. Skipping write."
            )
            return True  # treat as success since the item is already there

        # if it doesn't exist, write it
        table.put_item(Item=winner)
        print(
            f"Successfully wrote winner for {winner['ticker']} on {winner['date']} to DynamoDB."
        )
        return True

    except Exception as e:
        print(f"Error writing winner to DynamoDB: {e}")
        return False
