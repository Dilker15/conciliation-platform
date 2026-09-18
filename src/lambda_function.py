import json

def lambda_handler(event, context):
    
    file_id = event["file_id"]
    queries = event["query_executions"]



    return {
        'statusCode': 200,
        'body': json.dumps({
            "queries":queries,
            "file_id":file_id
        })
    }
