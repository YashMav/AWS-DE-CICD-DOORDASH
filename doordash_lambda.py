import json
import boto3
import pandas as pd
import datetime


def lambda_handler(event, context):
    # TODO implement
    sns_arn = "arn:aws:sns:ap-south-1:891376943331:aws-de-1-sns-doordash"
    print(f"Event -> {event}")
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    bucket_name_trg = 'aws-de-1-doordash-target-zn'
    date_var = datetime.datetime.today().strftime('%Y-%m-%d')
    file_name = f"processed_data/{date_var}_processed_data.csv"
    print(bucket)
    print(key)
    try:
        s3_client = boto3.client('s3')
        sns_client = boto3.client('sns')
        df = pd.DataFrame(columns=['id','status','amount','date'])
        s3_read = s3_client.get_object(Bucket=bucket, Key=key)
        file_content = s3_read['Body'].read().decode('utf-8').split('\r\n')
        for row in file_content:
            my_dict = json.loads(row)
            df.loc[my_dict['id']] = my_dict

        f = (df['status'] == 'delivered')
        df_dev = df.loc[f]
        count = df_dev['id'].count()

        df_dev.to_csv('/tmp/test.csv',index=False)
        print('/tmp/test.csv file created !!')
        lambda_path = '/tmp/test.csv'
        s3_trg = boto3.resource('s3')
        bucket_trg = s3_trg.Bucket(bucket_name_trg)
        bucket_trg.upload_file('/tmp/test.csv' , file_name)
        Message= f"The file {file_name} with records '{count}' is created in bucket {bucket_name_trg}"
        Subject = f"File processing successful !!"
        response = sns_client.publish(Subject=Subject  , Message =Message , TargetArn = sns_arn ,MessageStructure='text')
        print("Lambda function completed !!!")

    except Exception as e:
        print(e)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
