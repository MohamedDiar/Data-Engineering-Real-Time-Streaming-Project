#------modules/azure_event_hub_namespace/main.tf------

resource "azurerm_eventhub_namespace" "glucose_events" {
  name                = "glucose-events"
  resource_group_name = var.resource_group_name_in
  location            = var.location_in
  sku                 = var.ev_sku_name_in
  capacity            = var.ev_capacity_in
  auto_inflate_enabled = var.auto_inflate_enabled_in
  maximum_throughput_units = var.max_throughput_units_in

  provisioner "local-exec" {
    command = <<EOT
    echo "" >> "${path.root}/../.env"
    echo "#-----------Event Hub---------#" >> "${path.root}/../.env"
    echo "EVENT_HUB_CONNECTION_STR='${azurerm_eventhub_namespace.glucose_events.default_primary_connection_string}'" >> "${path.root}/../.env"
    echo "METRIC_EVENT_HUB_NAME='${var.event_hub_names_in[0]}'" >> "${path.root}/../.env"
    echo "DEVICE_EVENT_HUB_NAME='${var.event_hub_names_in[1]}'" >> "${path.root}/../.env"
    echo "STREAMLIT_CONS_GROUP='${var.event_hub_configs_in.raw_glucose_readings.consumer_groups[2]}'" >> "${path.root}/../.env"
    EOT
  }
}

module "azure_event_hubs" {
  source                 = "./azure_event_hubs"
  namespace_name_in      = azurerm_eventhub_namespace.glucose_events.name
  resource_group_name_in = var.resource_group_name_in
  event_hub_config_in    = var.event_hub_configs_in
}