#------modules/azure_databricks/oupouts.tf------

output "databricks_workspace_id_out" {
  value = azurerm_databricks_workspace.iot_glucose_streaming_workspace.id
}

output "databricks_workspace_host_out" {
  value = azurerm_databricks_workspace.iot_glucose_streaming_workspace.workspace_url
}