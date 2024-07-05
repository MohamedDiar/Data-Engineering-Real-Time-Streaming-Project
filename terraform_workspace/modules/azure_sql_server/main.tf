#------modules/azure_sql_server/main.tf------

# Generating random value for the name
resource "random_string" "name" {
  length  = 8
  lower   = true
  numeric = false
  special = false
  upper   = false
}

# Generating random value for the login password
resource "random_password" "password" {
  length           = 8
  lower            = true
  min_lower        = 1
  min_numeric      = 1
  min_special      = 1
  min_upper        = 1
  numeric          = true
  override_special = "_"
  special          = true
  upper            = true
}

#
resource "azurerm_mysql_flexible_server" "sql_server" {
  name                         = var.sql_server_name_in
  resource_group_name          = var.resource_group_name_in
  location                     = var.location_in
  administrator_login          = random_string.name.result
  administrator_password       = random_password.password.result
  backup_retention_days        = var.backup_retention_days_in
  geo_redundant_backup_enabled = false
  sku_name                     = var.sku_name_in
  version                      = "8.0.21"
  storage {
    auto_grow_enabled = var.storage_config_in.auto_growth
    iops              = var.storage_config_in.iops
    size_gb           = var.storage_config_in.size_gb
  }


  lifecycle {
    # prevent_destroy = true
    ignore_changes = [zone]
  }
}


resource "azurerm_mysql_flexible_server_configuration" "sql_server_configuration" {
  for_each            = var.server_parameters_in
  name                = each.value.name
  resource_group_name = var.resource_group_name_in
  server_name         = azurerm_mysql_flexible_server.sql_server.name
  value               = each.value.value
}

data "external" "my_ip" {
  program = ["bash", "${path.module}/get_ip.sh"]
}

module "firewall_rules" {
  source              = "./firewall_rule"
  resource_group_name = var.resource_group_name_in
  server_name         = azurerm_mysql_flexible_server.sql_server.name
  firewall_rules_in = concat(var.firewall_rules_in, [
    {
      name             = "AllowMyCurrentIP"
      start_ip_address = data.external.my_ip.result.public_ip
      end_ip_address   = data.external.my_ip.result.public_ip
    }
  ])
}
