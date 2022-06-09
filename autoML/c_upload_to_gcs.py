from google.cloud import storage
from a_get_data import data
from b_create_bucket import bkt_name

# encode data
data = data.to_csv(index=False).encode()

# Assign arguments to variables
destination_bucket_name = bkt_name
destination_blob_name = 'bitcoin_prices.csv'

def upload_blob_from_memory(destination_bucket_name, contents, destination_blob_name):
    """Uploads a file to the bucket."""

    # The contents to upload to the file
    contents = data

    storage_client = storage.Client()
    bucket = storage_client.bucket(destination_bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents)

    print(
        f"{destination_blob_name} uploaded to {destination_bucket_name}"
    )
    return destination_bucket_name, destination_blob_name

bucket_name, blob_name =  upload_blob_from_memory(destination_bucket_name, data, destination_blob_name)
gcs_source = f'{bucket_name}.{blob_name}'