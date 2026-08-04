import json

def lambda_handler(event, context):
    print("this is docker lambda and sqs messages")
    print(json.dumps(event, indent=2))
    print("this is docker lambda and sqs messages")
    return {
        "statusCode": 200
    }
