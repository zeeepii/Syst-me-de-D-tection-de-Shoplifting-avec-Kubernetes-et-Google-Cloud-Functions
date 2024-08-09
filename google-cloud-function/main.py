import base64
import os
import shutil
from google.cloud import storage
from kubernetes import client
from google.oauth2 import service_account
import google.auth.transport.requests
from google.cloud import pubsub_v1

def setup_kubernetes_client():
    # Chargez les credentials du service account
    credentials = service_account.Credentials.from_service_account_file(
        '/tmp/keys/service-account-key.json',
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )

    # Créez un client Kubernetes authentifié
    configuration = client.Configuration()
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    configuration.api_key = {"authorization": "Bearer " + credentials.token}
    configuration.host = "https://container.googleapis.com"
    client.Configuration.set_default(configuration)

    return client.CustomObjectsApi()

# Configuration Google Cloud Storage
storage_client = storage.Client()

def create_client_resource(client_id, xml_content):
    client_resource = {
        "apiVersion": "shoplift.example.com/v1",
        "kind": "Client",
        "metadata": {
            "name": client_id
        },
        "spec": {
            "clientId": client_id,
            "xmlConfig": xml_content
        }
    }
    return client_resource

def apply_client_resource(k8s_api, client_resource):
    try:
        k8s_api.create_namespaced_custom_object(
            group="shoplift.example.com",
            version="v1",
            namespace="default",
            plural="clients",
            body=client_resource
        )
        print(f"Applied client resource for {client_resource['metadata']['name']}")
    except client.rest.ApiException as e:
        if e.status == 409:  # Conflict, resource already exists
            k8s_api.patch_namespaced_custom_object(
                group="shoplift.example.com",
                version="v1",
                namespace="default",
                plural="clients",
                name=client_resource['metadata']['name'],
                body=client_resource
            )
            print(f"Updated client resource for {client_resource['metadata']['name']}")
        else:
            raise

def process_client_config(event, context):
    """Cloud Function triggered by a change to a Cloud Storage bucket."""
    # Créez le répertoire /tmp/keys s'il n'existe pas
    os.makedirs('/tmp/keys', exist_ok=True)
    
    # Copiez le fichier de clé
    shutil.copy('service-account-key.json', '/tmp/keys/service-account-key.json')

    # Setup Kubernetes client
    k8s_api = setup_kubernetes_client()

    file = event
    bucket_name = file['bucket']
    file_name = file['name']

    if not file_name.endswith('.xml'):
        print(f"Skipping non-XML file: {file_name}")
        return

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Download the file content
    xml_content = blob.download_as_text()
    
    # Extract client ID from file name
    client_id = os.path.splitext(os.path.basename(file_name))[0]

    # Create and apply the client resource
    client_resource = create_client_resource(client_id, xml_content)
    apply_client_resource(k8s_api, client_resource)

    # Move the processed file to a 'processed' folder
    new_blob = bucket.blob(f"processed/{file_name}")
    bucket.copy_blob(blob, bucket, new_blob.name)
    blob.delete()

    print(f"Processed and moved file: {file_name}")

def handle_gcs_notification(event, context):
    """Cloud Function to be triggered by Pub/Sub messages."""
    # Créez le répertoire /tmp/keys s'il n'existe pas
    os.makedirs('/tmp/keys', exist_ok=True)
    
    # Copiez le fichier de clé
    shutil.copy('service-account-key.json', '/tmp/keys/service-account-key.json')

    # Setup Kubernetes client
    k8s_api = setup_kubernetes_client()

    if 'data' in event:
        data = base64.b64decode(event['data']).decode('utf-8')
        # Parse the data as needed
        # This is a simplified example; you might need to adjust based on the actual message format
        file_data = {
            'bucket': 'your-bucket-name',
            'name': data
        }
        process_client_config(file_data, context)