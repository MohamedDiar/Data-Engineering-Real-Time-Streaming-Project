#-------/modules/azure_sql_server/firewall_rule/variables.tf--------

variable "server_name" {}
variable "resource_group_name" {}

variable "firewall_rules_in" {
  type = list(object({
    name             = string
    start_ip_address = string
    end_ip_address   = string
  }))
}
