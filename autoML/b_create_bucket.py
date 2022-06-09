import uuid
from google.cloud import storage

# Assign arguments to useful variables
project_id = 'ssi-amara-sandbox'
bucket_name = 'crypto'
bucket_location = 'us-central1'
bucket_class = 'STANDARD'

# Define method to create a GCS bucket
def create_bucket_class_location(bucket_name, bucket_location, bucket_class):
    """
    Create a new bucket in the US region with the standard storage
    class
    """
    bucket_suffix = str(uuid.uuid4())[:8]
    bucket_name = '-'.join([bucket_name, project_id, bucket_suffix])

    # Initialize the Storage Client
    storage_client = storage.Client()

    # fetch from GCS [Dry-run | Real-run]

    bucket = storage_client.bucket(bucket_name)
    bucket.storage_class = bucket_class
    try:
        new_bucket = storage_client.create_bucket(bucket, location=bucket_location)

        print(
            f"Created bucket {new_bucket.name} in {new_bucket.location} with storage class {new_bucket.storage_class}"
        )
        return new_bucket.name, new_bucket.location

    except Exception as e:
        print(f'{e}')
        return e

bkt_name, bkt_location = create_bucket_class_location(bucket_name, bucket_location, bucket_class)
# print(bkt_name)
# print(bkt_location)