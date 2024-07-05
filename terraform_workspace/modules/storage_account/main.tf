#-------modules/storage_account/main.tf-------

resource "azurerm_storage_account" "az_storage_account" {
  name                     = var.storage_account_name_in
  resource_group_name      = var.resource_group_name_in
  location                 = var.location_in
  account_tier             = var.account_tier_in
  account_replication_type = var.account_replication_type_in
}

resource "azurerm_storage_container" "az_storage_container" {
  name                  = "glucosefeeds"
  storage_account_name  = azurerm_storage_account.az_storage_account.name
  container_access_type = "blob"

  provisioner "local-exec" {
    command = <<EOT
    echo "" >> "${path.root}/../.env"
    echo "#-----------Storage Account---------#" >> "${path.root}/../.env"
    echo "account_name='${azurerm_storage_account.az_storage_account.name}'" >> "${path.root}/../.env"
    echo "container_name='${azurerm_storage_container.az_storage_container.name}'" >> "${path.root}/../.env"
    echo "account_key='${azurerm_storage_account.az_storage_account.primary_access_key}'" >> "${path.root}/../.env"
    echo "connection_string='${azurerm_storage_account.az_storage_account.primary_connection_string}'" >> "${path.root}/../.env"
    EOT
  }

}

