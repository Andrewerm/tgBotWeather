import logging

import boto3


async def handler(event, context):
    resource = boto3.resource(service_name='dynamodb',
                              endpoint_url='https://docapi.serverless.yandexcloud.net/ru-central1/b1g8130k4vibp9h9vg5q'
                                           '/etnste7l5gupmqs8ljrc',
                              region_name='ru-central',
                              )
    client = resource.meta.client
    logging.warning(client.list_tables())
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'isBase64Encoded': False,
        'body': 'Hello, {}!'.format(client.list_tables())
    }
