from pulumi_azure_native import resources, storage, web
from pulumi import ComponentResource, ResourceOptions, Output

# Create Resource Group Function
def resource_group(environment: str, location: str, workload: str):
    rg = resources.ResourceGroup(
        f'rg-{workload}-{environment}-001',
        resource_group_name=f'rg-{workload}-{environment}-001',
        location=location
    )
    return rg

# Create Storage Account Function
def storage_account(rg_name:str, location: str, sa_name: str):
    storage_account = storage.StorageAccount(
        f'{sa_name}',
        account_name=sa_name,
        resource_group_name=rg_name,
        location=location,
        sku=storage.SkuArgs(
            name=storage.SkuName.STANDARD_GRS
        ),
        kind=storage.Kind.STORAGE_V2
    )
    return storage_account

# Create Consumption Plan + Azure Function + Function Settings
def function(rg_name:str, environment: str, location: str, workload: str, storage_args: list):
    
    app_service_plan = web.AppServicePlan(
        f'asp-{workload}-{environment}-{location}-001',
        name=f'asp-{workload}-{environment}-{location}-001',
        resource_group_name=rg_name,
        location=location,
        kind='linux',
        reserved=True,
        sku=web.SkuDescriptionArgs(
            name='Y1',
            tier='Dynamic',
            size='Y1',
            family='Y'
        )
    )
    
    function = web.WebApp(
        f'func-{workload}-{environment}-{location}-001',
        name=f'func-{workload}-{environment}-{location}-001',
        resource_group_name=rg_name,
        location=location,
        kind='functionapp,linux',
        reserved=True,
        server_farm_id=app_service_plan.id,
        identity=web.ManagedServiceIdentityArgs(
            type=web.ManagedServiceIdentityType.SYSTEM_ASSIGNED,
        ),
        site_config=web.SiteConfigArgs(
            linux_fx_version="python|3.11"
        )
    )

    function_app_settings = web.WebAppApplicationSettings(
        f'func-{workload}-{environment}-{location}-001-settings',
        name=function.name,
        resource_group_name=rg_name,
        properties={
            "AzureWebJobsStorage": storage_args[0]['connection_string'],
            "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING": storage_args[0]['connection_string'],
            "WEBSITE_CONTENTSHARE": storage_args[0]['fileshare'],
            "FUNCTIONS_WORKER_RUNTIME": "python",
            "FUNCTIONS_EXTENSION_VERSION": "~4",
            "ObjectStorageConnection": storage_args[1]['connection_string'],
            "ObjectTableStorageName": storage_args[1]['table'],
            "ObjectContainerStorageName": storage_args[1]['container']
        }
    )


class ServerlessArgs:
    def __init__(self, environment: str, location: str, app_name: str, storage_accounts: list):
        self.environment = environment
        self.location = location
        self.app_name = app_name
        self.storage_accounts = storage_accounts


class ServerlessApp(ComponentResource):
    def __init__(self, name: str, args: ServerlessArgs, opts: ResourceOptions = None):
        super().__init__('azure:application:serverless', name, {}, opts)

        rg = resource_group(args.environment, args.location, args.app_name)

        #minimum of 1 storage account required for function app. loop allows us to create 1 + n storage accounts if necessary
        storage_accounts_properties = []
        for sa in args.storage_accounts:
            account = storage_account(rg.name, args.location, sa['name'])
            if 'container' in sa:
                container = storage.BlobContainer(sa['container'],
                                            container_name=sa['container'], 
                                            account_name=account.name,
                                            resource_group_name=rg.name)
            else:
                container = None
            
            if 'table' in sa:
                table = storage.Table(sa['table'],
                                            table_name=sa['table'], 
                                            account_name=account.name,
                                            resource_group_name=rg.name)
            else: 
                table = None
            
            # Get primary storage account key
            primary_storage_key = Output.secret(Output.all(rg.name, account.name)\
                .apply(lambda args: storage.list_storage_account_keys(
                    resource_group_name=args[0],
                    account_name=args[1]).keys[0].value))

            # Construct the connection string and output as secret
            connection_string = Output.secret(Output.all(account.name, primary_storage_key)\
                .apply(lambda args: f"DefaultEndpointsProtocol=https;AccountName={args[0]};AccountKey={args[1]};EndpointSuffix=core.windows.net"))
            
            #Create a list of storage account properties which gets passed to the azure function create function
            storage_accounts_properties.append(
                {
                    "name": account.name,
                    "connection_string": connection_string,
                    "container": getattr(container, 'name', None),
                    "table": getattr(table, 'name', None),
                    "fileshare": sa.get('fileshare', None)
                }
            ) 

        azure_function = function(rg.name, args.environment, args.location, args.app_name, storage_accounts_properties)

