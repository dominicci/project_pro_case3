# Predicting Bitcoin prices

In this Bitcoin prediction project, Vertex AI AutoML will be used to predict the future price of bitcoin.

The cloud technologies used in this project will include Google Cloud Storage (GCS), Cloud BigQuery and Vertex AI AutoML

Automated Machine Learning or AutoML is a no-code solution to build ML models on Vertex AI.
AutoML uses Transfer Learning and Neural Architect Search to train high quality machine learning models with minimal effort, and requires little machine learning expertise. However it requires at least 1,000 data points in a dataset.

## Requirements/Tools
~~~
python -m pip install requirements.txt
~~~

## Folder Structure
~~~
├── ./autoML
│   ├── ./autoML/README.md                 - Read code instructions.  
│   ├── ./autoML/a_get_data.py             - code to get data from yfinance.   
│   ├── ./autoML/b_create_bucket.py        - code to create a bucket in google cloud.  
│   ├── ./autoML/c_upload_to_gcs.py        - code to upload data to google storage bucket. 
│   ├── ./autoML/d_create_ai_dataset.py    - code to create a dataset in vertex AI.
│   ├── ./autoML/e_create_bq_dataset.py    - code to create a BigQuery dataset.
│   ├── ./autoML/f_automl_model.py         - code to train an AutoML tabular forcasing model 
│   └── ./autoML/requirement.txt           - packages required to run the codes.
~~~

### Note: The code in the files are inder-dependent. f_automl_model.py calls a function in d_create_ai_dataset.py which calls a function in c_upload_to_gcs. c_upload_to_gcs also calls a function in b_create_bucket.py and b_create_bucket.py calls a_get_data.py. e_create_bq_dataset.py has to be run before f_automl_model.py.   

## step 1 - Data Collection
~~~
file - a_get_data.py
~~~

The data is pulled from [yahoo finance](https://finance.yahoo.com/?guccounter=1&guce_referrer=aHR0cHM6Ly93d3cuZ29vZ2xlLmNvbS8&guce_referrer_sig=AQAAADa7DTccwKbeJMVxM5U4uu-M55DCCSYUMRMgNn8XLZn1-DUZtiyuT2ZBJX42GP9FIqZMmZZwYek0ZgrlfV2BmXhfReZkrlBdufR5vn61BBNl81nB4iQQW6rucoSdTVxjuQXt7QsQoy5jl_Aclf34GjLD_GgYRJLUZPFhS1g3UJ3F), a platform that provides financial news, data and commentary including stock quotes, press releases and financial reports.  

We will create a python script to get live historical crypto data from yahoo finance using the yahoo [finance API](https://www.yahoofinanceapi.com/). 

## step 2 - Create a Google Cloud Storage bucket
~~~
file - b_create_bucket.py 
~~~ 
This step creates a storage bucket in Google cloud. Because a google storage bucket needs to be globally unique, the bucket name choice is joined with project_id and a randomly generated bucket_suffix.

## step 3 - Upload Data to GCS
~~~
file - c_upload_to_gcs.py  
~~~
The step uploads the data extracted in step 1 to the cloud storage bucket created in step 2.  
The data has to be encoded before the upload.  

## step 4 - create a dataset in vertex AI
~~~
file - d_create_ai_dataset.py  
~~~
The create a dataset in vertex AI. Managed dataset enables you to create a clear link between your data and the model. Its provides a descriptive statistics and automatic or manual splitting into train, test and validation sets.   

## step 5 - create a BigQuery dataset  
~~~~
file - e_create_bq_dataset.py
~~~~
This step creates a dataset in BigQuery. The output of the AutoMl model will be exported to this dataset after training.

## step 6 - train the autoML model
~~~
file - f_automl_model
~~~
This is the step where the model is trained.  