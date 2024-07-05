#------modules/azure_event_hub_namespace/azure_event_hubs/main.tf------


resource "azurerm_eventhub" "event_hub" {
  for_each            = var.event_hub_config_in
  name                = each.key
  namespace_name      = var.namespace_name_in
  resource_group_name = var.resource_group_name_in
  partition_count     = each.value.partition_count
  message_retention   = each.value.message_retention
}

locals {
  consumer_groups = flatten([
    for eh_name, eh_details in var.event_hub_config_in : [
      for idx, cg in eh_details.consumer_groups : {
        key                 = "${eh_name}_${idx}"
        eventhub_name       = eh_name
        consumer_group_name = cg
      }
    ]
  ])
}


resource "azurerm_eventhub_consumer_group" "consumer_group" {
  for_each = {
    for idx, val in local.consumer_groups : val.key => val
  }
  name                = each.value.consumer_group_name
  eventhub_name       = azurerm_eventhub.event_hub[each.value.eventhub_name].name
  namespace_name      = var.namespace_name_in
  resource_group_name = var.resource_group_name_in
}





