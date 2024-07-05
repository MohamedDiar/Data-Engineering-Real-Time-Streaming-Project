#------modules/azure_event_hub_namespace/azure_event_hubs/variables.tf------

variable "resource_group_name_in" {}
variable "namespace_name_in" {}

variable "event_hub_config_in" {
  type = map(object({
    partition_count   = number
    message_retention = number
    consumer_groups   = list(any)
  }))
}