#------modules/azure_sql_server/output.tf------
output "server_name_out" {
  description = "The name of the SQL Server."
  value       = azurerm_mysql_flexible_server.sql_server.name
}

output "host_name_out" {
  description = "The hostname of the SQL Server."
  value       = azurerm_mysql_flexible_server.sql_server.fqdn

}
output "admin_name_out" {
  description = "The admin name for the SQL Server."
  value       = azurerm_mysql_flexible_server.sql_server.administrator_login
}

output "server_password_out" {
  description = "The admin password for the SQL Server."
  value       = azurerm_mysql_flexible_server.sql_server.administrator_password
  sensitive   = true

}

