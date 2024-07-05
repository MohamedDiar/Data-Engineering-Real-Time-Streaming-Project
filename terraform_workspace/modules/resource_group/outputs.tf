#------modules/resource_group/outputs.tf------

output "resource_group_name_out" {
  value = azurerm_resource_group.resource_group.name
}

output "resource_group_location_out" {
  value = azurerm_resource_group.resource_group.location
}