import boto3
import os
import logging
import traceback
import json
import sys

# Global Variables, can be used across multiple iterations of function call
region = os.environ.get('REGION')
tagKey = os.environ.get('TAG_KEY')
tagValue = os.environ.get('TAG_VALUE')
ec2_client = boto3.client('ec2',region_name=region)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
instances = ec2_client.describe_instances(Filters=[{'Name': f'tag:{str(tagKey)}','Values':[str(tagValue),],}])

def lambda_handler(event, context):
    try:
        action = event['action']
        if (len(instances['Reservations']) == 0):
            raise ValueError('NO INSTANCES FOUND!')
        for instance in (instances['Reservations'][0]['Instances']):
            instanceid = instance['InstanceId']
            if action == "STOP":
                ec2_client.stop_instances(InstanceIds=[str(instanceid),])
                logger.info(f'Stopped instances: {instanceid}')
            elif action == "START":
                ec2_client.start_instances(InstanceIds=[str(instanceid),])
                logger.info(f'Started instances: {instanceid}')
            else:
                raise ValueError('Incorrect value for "action" variable. Please use "STOP" or "START"')
                logger.info(f'ec2 scheduler region: {str(region)}')
    except Exception as exp:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        traceback_string = traceback.format_exception(exception_type, exception_value, exception_traceback)
        err_msg = json.dumps({
            "errorType": exception_type.__name__,
            "errorMessage": str(exception_value),
            "stackTrace": traceback_string
        })
        logger.error(err_msg)
    return {
        'statusCode': 200
    }