#-------modules/resource_group/main.tf-------

#Creating a resource group
resource "azurerm_resource_group" "resource_group" {
  name     = var.resource_group_name_in
  location = var.location_in
  # lifecycle {
  #   prevent_destroy = true
  # }
}