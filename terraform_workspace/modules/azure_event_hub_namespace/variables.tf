#------modules/azure_event_hub/varibles.tf------

variable "resource_group_name_in" {}
variable "location_in" {}
variable "ev_sku_name_in" {}
variable "ev_capacity_in" {}
variable "auto_inflate_enabled_in" {}
variable "max_throughput_units_in" {}
variable "event_hub_names_in" {}

variable "event_hub_configs_in" {
  type = map(object({
    partition_count   = number
    message_retention = number
    consumer_groups   = list(any)
  }))
}