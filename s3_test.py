import boto3

try:
    # AWS 자격 증명은 자동으로 ~/.aws/credentials 에서 가져옵니다.
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    print("✅ Success! You are connected to AWS.")
    print("Your buckets:")
    for bucket in response['Buckets']:
        print(f"  - {bucket['Name']}")

except Exception as e:
    print("❌ Failed to connect to AWS.")
    print(f"Error: {e}")