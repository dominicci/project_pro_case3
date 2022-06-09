In this section, we will use cloud scheduler to schedule a cron job that will trigger a cloud function job which will run every monday at 9am. 

The cloud function job gets bitcoin historical data from from yfinance, create a storage bucket in GCS, uploads the data to the created bucket, creates a vertex ai tarbular forcasting dataset, creates a bigquery dataset (if not already existing) and finaly trains the model and outputs/predictions form the test set to bigquery.

Cloud Schedular -> Cloud Function -> Yfnance API -> Cloud Storage -> Vertex AI -> Bigquery

## Step 1 - Create and deploy a http Cloud Function trigger using Python

1. cd in to the cloud_fxn directory that contains the cloud function code.

~~~
cd autoML-cloud_fxn/cloud_fxn
~~~

The cloud_fxn directory contains two files  
main.py  - contains code that will be run by cloud fuction
requirements.txt - specifies code dependencies.

Note:

The entry point is the function run.  
The 'run' function contains an argument which is required for cloud function to execute http trigger function.  

Deploy the function.
To deploy the function with an HTTP trigger, run the following command in the cloud_fxn directory:
~~~
gcloud functions deploy run --runtime python39 --trigger-http --allow-unauthenticated
~~~

The --allow-unauthenticated flag lets you reach the function [without authentication](https://cloud.google.com/functions/docs/securing/managing-access-iam#allowing_unauthenticated_http_function_invocation). To require [authentication](https://cloud.google.com/functions/docs/securing/authenticating#developers), omit the flag.

For further details, visit the cloud function documentation:
[Creating a function](https://cloud.google.com/functions/docs/create-deploy-http-python#creating_a_function)

## step 2 - Create a Cloud Scheduler job with a http target.

The following command creates a job named my-job that sends a HTTP GET request to 'http://example.com/path' every Monday at 09:00:
~~~
gcloud scheduler jobs create http my-job --schedule="0 9 * * 1" --uri="http://example.com/path" --http-method=GET
~~~

Note - replace the uri with the link to the cloud function job you had created in step 1.
Navigate to cloud function in GCP console, 
Click on the cloud function job
Click on trigger and copy the trigger url. 
Replace "http://example.com/path" with the cloud function url.

## Code Explaination

The main.py contais a number of functions
* getdata() gets bitcoin data from yahoo finance.
* create_bucket_class_location() creates a cloud storage bucket
* upload_blob_from_memory() uploads the bitcoin data to the cloud storage bucket
* create_and_import_dataset_tabular_gcs() creates a vertex AI dataset
* create_bq_dataset() creates a BigQuery dataset
* create_training_pipeline_tabular_forecasting() creates an AutoML training job
* run() is the entry point for cloud functions