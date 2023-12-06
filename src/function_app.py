from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient, TableEntity
import azure.functions as func
import os

app = func.FunctionApp()

@app.blob_trigger(arg_name="blob", path="objectcontainer/{name}.{blobextension}",
                connection="ObjectStorageConnection") 

def main(blob: func.InputStream):
    
    # blob.name gets passed as 'container/blob' so we need to split and take last element
    blob_name = blob.name.split('/')[-1]
    connection_string = os.getenv('ObjectStorageConnection')
    container_name = os.getenv('ObjectContainerStorageName')
    table_name = os.getenv('ObjectTableStorageName')

    # Create an azure storage blob service client to establish a connection to the storage account
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Create blob instance and then get blob properties
    blob_instance = blob_service_client.get_blob_client(container_name, blob_name)
    blob_properties = blob_instance.get_blob_properties()

    # Create a azure storage table client
    table_service_client = TableServiceClient.from_connection_string(connection_string)

    # Get table client
    table_instance = table_service_client.get_table_client(table_name)

    # Create a new entity with blob properties
    new_entry = TableEntity(PartitionKey="blob", RowKey=blob_name, Timestamp=blob_properties.creation_time, BlobName=blob_name, BlobSize=blob_properties.size, ContentType=blob_properties.content_settings.content_type)

    # Add the new entity to the table
    table_instance.create_entity(new_entry)