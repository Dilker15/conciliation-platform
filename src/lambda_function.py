import json

def lambda_handler(event, context):
    print("This lambda was execute with a Docker Image")
    for record in event["Records"]:
        print("This is body Message : ",record["Body"])
    
    
