import yfinance as yf
import datetime as dt
import uuid
from google.cloud import storage
from google.cloud import aiplatform
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

# get data from yahoo finance
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

# Initialize bigquery
client = bigquery.Client()

# Assign arguments to variables
dataset_name = 'demo10'
bq_dataset_id = f'{client.project}.{dataset_name}'
dataset_location = 'us-central1'

def create_bq_dataset():

    
    dataset = bigquery.Dataset(bq_dataset_id)
    dataset.location = dataset_location

    #Check if the dataset already exists
    try:
        dataset = client.get_dataset(bq_dataset_id)
        if dataset:
            print(f'The dataset ID: {bq_dataset_id} already exists. Would proceed to train the model')
            

        # If the dataset does not exist, then create it
    except NotFound:
        client.create_dataset(dataset, timeout = 30)
        print(f"Created dataset {bq_dataset_id}")


# train autoML model
vertex_ai_dataset_id = create_and_import_dataset_tabular_gcs(display_name=display_name, project=project, location= location, gcs_source=gcs_source)

project = 'ssi-amara-sandbox'
display_name = 'model_1'
model_display_name = 'model_1'
target_column = 'Close'
time_series_identifier_column = 'Year'
time_column = 'Date'
unavailable_at_forecast = ['Open', 'High', 'Close', 'Low', 'Adj_Close', 'Volume',]
available_at_forecast = ['Date']
forecast_horizon = 1,000

table_name = 'evaluated_data_items'
destination_bigquery_uri = f'{bq_dataset_id}.{table_name}'
export_evaluated_data_items_config = {'destination_bigquery_uri': destination_bigquery_uri,
                                      'override_existing_table': True}

def create_training_pipeline_tabular_forecasting(
    project: str,
    display_name: str,
    vertex_ai_dataset_id: str,
    model_display_name: str,
    target_column: str,
    time_series_identifier_column: str,
    time_column: str,
    # time_series_attribute_columns: str,
    unavailable_at_forecast: str,
    available_at_forecast: str,
    forecast_horizon: int,
    export_evaluated_data_items_config,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
    
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PipelineServiceClient(client_options=client_options)
    # set the columns used for training and their data types
    transformations = [
        {"auto": {"column_name": "Date"}},
        {"auto": {"column_name": "Open"}},
        {"auto": {"column_name": "High"}},
        {"auto": {"column_name": "Low"}},
        {"auto": {"column_name": "Close"}},
        {"auto": {"column_name": "Adj_Close"}},
        {"auto": {"column_name": "Volume"}},
    ]

    data_granularity = {"unit": "day", "quantity": 1}

    # the inputs should be formatted according to the training_task_definition yaml file
    training_task_inputs_dict = {
        # required inputs
        "targetColumn": target_column,
        "timeSeriesIdentifierColumn": time_series_identifier_column,
        "timeColumn": time_column,
        "transformations": transformations,
        "dataGranularity": data_granularity,
        "optimizationObjective": "minimize-rmse",
        "trainBudgetMilliNodeHours": 1,
        # "timeSeriesAttributeColumns": time_series_attribute_columns,
        "unavailable_at_forecast_columns": unavailable_at_forecast,
        "available_at_forecast_columns": available_at_forecast,
        "forecastHorizon": forecast_horizon,
        # 'override_existing_table': True,
        "export_evaluated_data_items_config": export_evaluated_data_items_config,
    }

    training_task_inputs = json_format.ParseDict(training_task_inputs_dict, Value())

    training_pipeline = {
        "display_name": display_name,
        "training_task_definition": "gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_forecasting_1.0.0.yaml",
        "training_task_inputs": training_task_inputs,
        "input_data_config": {
            "dataset_id": vertex_ai_dataset_id,
            "fraction_split": {
                "training_fraction": 0.8,
                "validation_fraction": 0.1,
                "test_fraction": 0.1,
            },
        },
        "model_to_upload": {"display_name": model_display_name},
    }
    parent = f"projects/{project}/locations/{location}"
    response = client.create_training_pipeline(
        parent=parent, training_pipeline=training_pipeline
    )
    print("response:", response)    




def run(event):

    create_bq_dataset()
    
    create_training_pipeline_tabular_forecasting(
    project = project,
    display_name = display_name,
    dataset_id = vertex_ai_dataset_id,
    model_display_name = model_display_name,
    target_column = target_column,
    time_series_identifier_column = time_series_identifier_column,
    time_column = time_column,
    # time_series_attribute_columns: str,
    unavailable_at_forecast = unavailable_at_forecast,
    available_at_forecast = available_at_forecast,
    forecast_horizon = forecast_horizon,
    export_evaluated_data_items_config = export_evaluated_data_items_config)

    print('Task completed!')
    return 'Task completed!'

