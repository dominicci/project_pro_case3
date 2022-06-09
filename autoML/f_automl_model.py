from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from d_create_ai_dataset import vertex_ai_dataset_id
from e_create_bq_dataset import bq_dataset_id

project = 'ssi-amara-sandbox'
display_name = 'model_1'
dataset_id = vertex_ai_dataset_id
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
    dataset_id: str,
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
            "dataset_id": dataset_id,
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

if __name__ == "__main__":
    create_training_pipeline_tabular_forecasting(
    project = project,
    display_name = display_name,
    dataset_id = dataset_id,
    model_display_name = model_display_name,
    target_column = target_column,
    time_series_identifier_column = time_series_identifier_column,
    time_column = time_column,
    # time_series_attribute_columns: str,
    unavailable_at_forecast = unavailable_at_forecast,
    available_at_forecast = available_at_forecast,
    forecast_horizon = forecast_horizon,
    export_evaluated_data_items_config = export_evaluated_data_items_config,
)