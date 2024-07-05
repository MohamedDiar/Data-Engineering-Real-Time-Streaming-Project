#-------modules/function_app/variables.tf-------

variable "resource_group_name_in" {}
variable "service_plan_name_in" {}
variable "location_in" {}
variable "os_type_in" {}
variable "sku_name_in" {}

variable "storage_account_name_in" {}
variable "storage_account_access_key_in" {}


variable "sql_server_admin_in" {}
variable "sql_server_password_in" {}
variable "sql_database_name_in" {}
variable "hostname_in" {}
variable "port_in" {}

variable "event_hub_conn_str_in" {}
variable "schedule_expressions_in" {}
variable "redis_host_in" {}
variable "redis_port_in" {}
variable "redis_password_in" {}
variable "low_glucose_chat_id_in" {}
variable "high_glucose_chat_id_in" {}
variable "transmission_quality_chat_id_in" {}
variable "disconnected_error_chat_id_in" {}
variable "glucose_increasing_trend_in" {}
variable "device_alerts_bot_token_in" {}
variable "glucose_alerts_bot_token_in" {}

