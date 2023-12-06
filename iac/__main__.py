from modules.app import ServerlessApp, ServerlessArgs
from pulumi import Config

config = Config()

serverless_app = {  
    "name": "blobprocessor",
    "environment": config.require('environment'),
    "location": config.require('location'),
    "storage_accounts": [
        {
            "name": "sablobprocdev001",
            "container": "functioncontainer",
            "fileshare": "functionfileshare",
        },
        {
            "name": "sablobprocdev002",
            "container": "objectcontainer",
            "table": "objecttable"
        }
    ]
}

deploy_serverless_app = ServerlessApp('blobprocessor', 
                                    ServerlessArgs(serverless_app['environment'], 
                                    serverless_app['location'], 
                                    serverless_app['name'], 
                                    serverless_app['storage_accounts'])
                                    )
