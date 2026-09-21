import json

def lambda_handler(event, context):
    print("QUERIES EXECUTED BY APPLY RESULT CONCILIATED : ", event)
    return {
        'statusCode': 200,
        'body': json.dumps({
            "result":event,
            
        })
    }
