#-------module/azure_sql_database/outputs.tf-------

output "database_name_out" {
  description = "The name of the SQL Database."
  value       = azurerm_mysql_flexible_database.sql_database.name
}