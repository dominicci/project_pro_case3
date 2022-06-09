import yfinance as yf
import datetime as dt
import uuid
from google.cloud import storage
from google.cloud import aiplatform
from google.cloud import bigquery
from google.cloud.exceptions import NotFound


def getdata():
    #Set the cryptocurrency tickers to get the data
    crypto = 'BTC-USD'

    #Define the start and end date for the historical data
    today = dt.datetime.now()
    start = dt.datetime(2018, 1, 1,)
    end = dt.date(today.year, today.month, today.day)

    #Fetch bitcoin data using yfinance download function.
    data = yf.download(tickers=crypto, start=start, end=end, interval='1d',)

    data.rename(columns={'Adj Close':'Adj_Close'}, inplace=True)
    data = data.reset_index()
    data['Year'] = data['Date'].dt.year

    return data

data = getdata()

# encode data
data = data.to_csv(index=False).encode()

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

display_name = 'dataset1'
project = 'ssi-amara-sandbox'
location = 'us-central1'
gcs_source =  gcs_source

def create_and_import_dataset_tabular_gcs(
    display_name, project, location, gcs_source,):

    aiplatform.init(project=project, location=location)

    dataset = aiplatform.TimeSeriesDataset.create(
        display_name=display_name, gcs_source=gcs_source,
    )

    dataset.wait()

    print(f'\tDataset: "{dataset.display_name}"')
    print(f'\tname: "{dataset.resource_name}"')
    resource_name = dataset.resource_name
    dataset_id = resource_name.split('/')
    dataset_id = dataset_id[-1]
    return dataset_id



# Create dataset
def create_dataset():
    # Initialize bigquery
    client = bigquery.Client()

    # Assign arguments to variables
    dataset_name = 'demo10'
    bq_dataset_id = f'{client.project}.{dataset_name}'
    table_id = 'bitcoin_prices'
    dataset_location = 'us-central1'

    dataset = bigquery.Dataset(bq_dataset_id)
    dataset.location = dataset_location

    #Check if the dataset already exists
    try:
        dataset = client.get_dataset(bq_dataset_id)
        if dataset:
            print(f'The dataset ID: {bq_dataset_id} already exists. Proceed to train the model')
            

        # If the dataset does not exist, then create it
    except NotFound:
        client.create_dataset(dataset, timeout = 30)
        print(f"Created dataset {bq_dataset_id}")


def run(event):

    create_dataset()
    vertex_ai_dataset_id = create_and_import_dataset_tabular_gcs(display_name=display_name, project=project, location= location, gcs_source=gcs_source)
    
    print('Task completed!')
    return 'Task completed!'

