#-------modules/storage_account/outputs.tf-------


output "storage_account_name_out" {
  value = azurerm_storage_account.az_storage_account.name

}

output "account_key_out" {
  value = azurerm_storage_account.az_storage_account.primary_access_key
}

output "container_name_out" {
  value = azurerm_storage_container.az_storage_container.name
}