#------modules/azure_sql_server/variables.tf------

variable "resource_group_name_in" {
  description = "The name of the resource group in which the SQL Server will be created"
}

variable "location_in" {
  description = "The location in which the SQL Server will be created"
}

# variable "server_admin_login_in" {}
# variable "server_admin_password_in" {}

variable "sql_server_name_in" {}
variable "backup_retention_days_in" {}
variable "sku_name_in" {}

variable "storage_config_in" {}
variable "server_parameters_in" {}

variable "firewall_rules_in" {
  type = list(object({
    name             = string
    start_ip_address = string
    end_ip_address   = string
  }))
}