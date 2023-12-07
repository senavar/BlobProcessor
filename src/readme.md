# Azure Blob Storage Trigger Function

This Python script is an Azure Function that gets triggered when a new blob is added to a specified Azure Blob Storage container. 

## Functionality

When a new blob is added to the specified container, the function retrieves the blob's properties and stores them in an Azure Table Storage.

## How to Use

1. Set up your Azure Blob Storage and Azure Table Storage.
2. Set the following environment variables via application settings:
    - `ObjectStorageConnection`: The connection string for your Azure Storage account.
    - `ObjectContainerStorageName`: The name of the blob container in your Azure Storage account.
    - `ObjectTableStorageName`: The name of the table in your Azure Table Storage.
3. Deploy this function to your Azure Functions app.

## Code Overview

The function is triggered by a `blob_trigger` event. The `blob_trigger` is configured to watch the blob container specified by the `ObjectContainerStorageName` environment variable.

When a new blob is added to the container, the function is triggered and the blob's name and data are passed to the `main` function.

The `main` function splits the blob's name to get the actual name of the blob (without the container name). It then creates a `BlobServiceClient` to connect to the Azure Storage account and a `TableServiceClient` to connect to the Azure Table Storage.

The function gets the properties of the blob using the `get_blob_properties` method of the `BlobServiceClient`. It then creates a new `TableEntity` with these properties and adds it to the table in the Azure Table Storage using the `create_entity` method of the `TableServiceClient`.

## Dependencies

This script requires the following Python packages:

- `azure-functions`
- `azure-storage-blob`
- `azure-data-tables`
