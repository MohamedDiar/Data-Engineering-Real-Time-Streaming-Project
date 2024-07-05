#------modules/azure_event_hub/output.tf------

output "namespace_name_rule_connection_string_out" {
  value = azurerm_eventhub_namespace.glucose_events.default_primary_connection_string
}
