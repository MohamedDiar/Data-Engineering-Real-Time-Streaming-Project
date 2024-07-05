#------modules/azure_sql_database/main.tf------

resource "azurerm_mysql_flexible_database" "sql_database" {
  name                = var.sql_database_name_in
  resource_group_name = var.resource_group_name_in
  server_name         = var.server_name_in
  collation           = var.collation_in
  charset             = "utf8"


  provisioner "local-exec" {
    command = <<EOT
    echo "" >> "${path.root}/../.env"
    echo "#-----------SQL Database---------#" >> "${path.root}/../.env"
    echo "host='${var.hostname_in}'" >> "${path.root}/../.env"
    echo "port=${var.port_in}" >> "${path.root}/../.env"
    echo "database='${azurerm_mysql_flexible_database.sql_database.name}'" >> "${path.root}/../.env"
    echo "user='${var.username_in}'" >> "${path.root}/../.env"
    echo "password='${var.password_in}'" >> "${path.root}/../.env"
    EOT
  }

  lifecycle {
    ignore_changes = [
      collation, charset
    ]

  }
}

# resource "null_resource" "create_envfile" {
#   depends_on = [ azurerm_mysql_flexible_database.sql_database ]

#   provisioner "local-exec" {
#     command = "echo 'HOST_NAME=${azurerm_mysql_flexible_database.sql_database.fqdn}\nDATABASE_NAME=${azurerm_mysql_flexible_database.sql_database.name}\nUSERNAME=${azurerm_mysql_flexible_database.sql_database.administrator_login}\nPASSWORD=${azurerm_mysql_flexible_database.sql_database.administrator_login_password}' > .env"

#   }
# }
