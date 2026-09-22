import json

def lambda_handler(event, context):
    queries_id = event["query_executions"]
    print("QUERIES RESULT FROM CHECK STATUS QUERIES : ",queries_id)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            "queries":queries_id
        })
    }
