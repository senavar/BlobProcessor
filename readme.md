# BlobProcessor

## Design Prompt: 
At a minimum your Pulumi application code should consist of:
- A storage bucket
- A database table
- A serverless function that processes object uploads and writes the object key and a
timestamp to the database table
- A ComponentResource that appropriately encapsulates two or more of the resources to
illustrate reusability


## Success criteria:
- Should be able to upload a file to the bucket and see the database entry get created

## Design decisions:
- 2x Azure Storage Accounts 
    - one for: Function runtime (container) and other for content (fileshare)
    - one for: uploads of objects (container) and also a Table Storage 
- Azure Function - Consumption Plan

## Tradeoffs: 
- Using Azure Table Storage as a low-cost, easy deployment for database tables
    - One of the Azure Database PaaS options could be more of an appropriate option. But due to time (<4 hours) and complexity of getting tables/schema/access properly set up for what is trying to be accomplished here, decided against it.
- Using Azure blob storage trigger instead of event or queue based for simplicity but can have high latency
    - event based would best for low latency

## Areas of improvement if had more hours: 
- leverage private endpoints and vnet integration 
- add dynamic namme creation/checking to ensure naming limitations are not met (i.e. storage account character limit)
- deploy Azure SQL DB, automate SQL DB init, automatically adding Azure Function - System Assigned Identity to access SQL db 
- implement event based triggering 
- use azure key vault and secret strings to properly store connection strings 
- containerize to make it portable to other platforms like container apps 
