#---------modules/azure_databricks/providers.tf---------

terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "1.48.2"
    }
  }
}

provider "databricks" {

  host                        = azurerm_databricks_workspace.iot_glucose_streaming_workspace.workspace_url
  azure_workspace_resource_id = azurerm_databricks_workspace.iot_glucose_streaming_workspace.id
}

