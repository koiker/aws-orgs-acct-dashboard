import csv
import logging
import os
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger('S3batchCopy')
logger.addHandler(logging.StreamHandler())
logger.setLevel(getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))
DESTINATION_BUCKET = os.getenv('DESTINATION_BUCKET')
os.chdir('/tmp')


def handler(event, context):
    client = boto3.client('organizations')
    present = datetime.now()
    past_24_months = [0 for _ in range(24)]

    try:
        logger.info('Getting the list of AWS accounts from Organizations')
        resp = client.list_accounts()
        accounts = resp['Accounts']
        while next_token := resp.get('NextToken'):
            resp = client.list_accounts(NextToken=next_token)
            accounts += resp['Accounts']
        csv_columns = ['month', 'total_accounts']
        csv_file = 'accounts.csv'
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()  # Remove this line if you don't want to add the csv header to the file
            for account in accounts:
                if account['Status'] == 'ACTIVE':
                    account['JoinedTimestamp'] = account['JoinedTimestamp'].replace(tzinfo=None)
                    diff_in_days = present - account['JoinedTimestamp']
                    month = int(diff_in_days.days / 30)
                    if month < 24:
                        past_24_months[month] += 1
                    logger.debug(account)
            logger.debug(past_24_months)
            for i in range(24):
                writer.writerow({'month': i, 'total_accounts': past_24_months[i]})
        logger.info(f'Sending the file to S3 bucket: {DESTINATION_BUCKET}')
        s3 = boto3.client('s3')
        with open(csv_file, 'rb') as data:
            s3.upload_fileobj(data, DESTINATION_BUCKET, csv_file)
        logger.info('Completed the file upload!')
    except ClientError as e:
        logger.exception(f'Unable to get account list from Orgs. Error: {e}')


if __name__ == '__main__':
    mock_event = object
    mock_context = object
    handler(mock_event, mock_context)
