#-------/modules/azure_sql_server/firewall_rule/main.tf--------

resource "azurerm_mysql_flexible_server_firewall_rule" "firewall_rule" {
  for_each            = { for rule in var.firewall_rules_in : rule.name => rule }
  name                = each.value.name
  resource_group_name = var.resource_group_name
  server_name         = var.server_name
  start_ip_address    = each.value.start_ip_address
  end_ip_address      = each.value.end_ip_address
  # lifecycle {
  #   prevent_destroy = true
  # }
}
