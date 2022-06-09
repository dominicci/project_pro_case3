from google.cloud import aiplatform
from c_upload_to_gcs import gcs_source


display_name = 'dataset1'
project = 'ssi-amara-sandbox'
location = 'us-central1'
gcs_source =  gcs_source

def create_and_import_dataset_tabular_gcs(
    display_name, project, location, gcs_source,
):

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

vertex_ai_dataset_id = create_and_import_dataset_tabular_gcs(display_name=display_name, project=project, location= location, gcs_source=gcs_source)