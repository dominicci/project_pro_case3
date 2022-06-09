from google.cloud import bigquery
from google.cloud.exceptions import NotFound

# Initialize bigquery
client = bigquery.Client()

# Assign arguments to variables
dataset_name = 'demo10'
bq_dataset_id = f'{client.project}.{dataset_name}'
table_id = 'bitcoin_prices'
dataset_location = 'us-central1'

# Create dataset
def create_dataset():

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

        
if __name__ == "__main__":
    create_dataset()