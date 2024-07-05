#------root/main.tf------

# Modules for all the needed resources

module "resource_group" {
  source                 = "./modules/resource_group"
  resource_group_name_in = var.resource_name
  location_in            = var.location
}

module "storage_account" {
  source                      = "./modules/storage_account"
  storage_account_name_in     = var.storage_account_name
  resource_group_name_in      = module.resource_group.resource_group_name_out
  location_in                 = module.resource_group.resource_group_location_out
  account_tier_in             = var.account_tier
  account_replication_type_in = var.account_replication_type
}

module "azure_sql_server" {
  source                   = "./modules/azure_sql_server"
  resource_group_name_in   = module.resource_group.resource_group_name_out
  location_in              = module.resource_group.resource_group_location_out
  sql_server_name_in       = var.sql_server_name
  backup_retention_days_in = var.sql_server_backup_retention_days
  sku_name_in              = var.sql_server_sku_name
  storage_config_in = {
    auto_growth = var.storage_config.auto_growth
    size_gb     = var.storage_config.size_gb
    iops        = var.storage_config.iops
  }
  server_parameters_in = var.server_configs
  firewall_rules_in = [
    {
      name             = "AllowAllAzureIps"
      start_ip_address = "0.0.0.0"
      end_ip_address   = "0.0.0.0"
    }
  ]
}

module "azure_database" {
  source                 = "./modules/azure_sql_database"
  sql_database_name_in   = var.sql_database_name
  resource_group_name_in = module.resource_group.resource_group_name_out
  server_name_in         = module.azure_sql_server.server_name_out
  hostname_in            = module.azure_sql_server.host_name_out
  collation_in           = var.sql_database_collation
  username_in            = module.azure_sql_server.admin_name_out
  password_in            = module.azure_sql_server.server_password_out
  port_in                = var.MYSQL_port

  #Explicitely defining the dependency to ensure nested module "firewall_rules" in azure_sql_server is executed in case of -target
  depends_on = [module.azure_sql_server]
}

module "azure_redis_cache" {
  source                 = "./modules/azure_redis_cache"
  resource_group_name_in = module.resource_group.resource_group_name_out
  location_in            = module.resource_group.resource_group_location_out
  cache_name_in          = var.cache_name
  capacity_in            = var.cache_capacity
  family_in              = var.cache_family
  sku_name_in            = var.cache_sku_name

  # depends_on = [module.azure_database]
}

module "event_hub" {
  source                 = "./modules/azure_event_hub_namespace"
  resource_group_name_in = module.resource_group.resource_group_name_out
  location_in            = module.resource_group.resource_group_location_out
  ev_sku_name_in         = var.ev_sku_name
  ev_capacity_in         = var.ev_capacity
  auto_inflate_enabled_in = var.auto_inflate_enabled
  max_throughput_units_in = var.max_throughput_units
  event_hub_names_in     = var.event_hub_names
  event_hub_configs_in   = var.event_hub_configs

}

module "azure_networking" {
  source                 = "./modules/azure_networking"
  resource_group_name_in = module.resource_group.resource_group_name_out
  location_in            = module.resource_group.resource_group_location_out
  vnet_configs_in        = var.vnet_configs
  subnet_configs_in      = var.subnet_configs
  nic_configs_in         = var.nic_configs
  security_group_name_in = var.security_group_name
}

module "azure_vm" {
  source                  = "./modules/azure_vm"
  resource_group_name_in  = module.resource_group.resource_group_name_out
  location_in             = module.resource_group.resource_group_location_out
  vm_name_in              = var.vm_name
  vm_size_in              = var.vm_size
  admin_username_in       = var.admin_username
  network_interface_id_in = module.azure_networking.network_interface_id_out
  os_disk_configs_in      = var.os_disk_configs
  vm_image_configs_in     = var.source_image_configs
  ssh_key_name_in         = var.ssh_key_name
  event_hub_conn_str_in   = module.event_hub.namespace_name_rule_connection_string_out
  hostname_in             = module.azure_sql_server.host_name_out
  port_in                 = var.MYSQL_port
  sql_server_admin_in     = module.azure_sql_server.admin_name_out
  sql_server_password_in  = module.azure_sql_server.server_password_out
  sql_database_name_in    = module.azure_database.database_name_out


  depends_on = [module.azure_networking]

}

module "function_app" {
  source                          = "./modules/function_app"
  resource_group_name_in          = module.resource_group.resource_group_name_out
  location_in                     = module.resource_group.resource_group_location_out
  service_plan_name_in            = var.service_plan_name
  os_type_in                      = var.os_type
  sku_name_in                     = var.sku_name
  storage_account_name_in         = module.storage_account.storage_account_name_out
  storage_account_access_key_in   = module.storage_account.account_key_out
  hostname_in                     = module.azure_sql_server.host_name_out
  sql_database_name_in            = module.azure_database.database_name_out
  port_in                         = var.MYSQL_port
  sql_server_admin_in             = module.azure_sql_server.admin_name_out
  sql_server_password_in          = module.azure_sql_server.server_password_out
  event_hub_conn_str_in           = module.event_hub.namespace_name_rule_connection_string_out
  schedule_expressions_in         = var.schedule_expressions
  redis_host_in                   = module.azure_redis_cache.host_name_out
  redis_port_in                   = module.azure_redis_cache.ssl_port_out
  redis_password_in               = module.azure_redis_cache.primary_access_key_out
  low_glucose_chat_id_in          = local.envs["LOW_GLUCOSE_CHAT_ID"]
  high_glucose_chat_id_in         = local.envs["HIGH_GLUCOSE_CHAT_ID"]
  transmission_quality_chat_id_in = local.envs["TRANSMISSION_QUALITY_CHAT_ID"]
  disconnected_error_chat_id_in   = local.envs["DISCONNECTED_ERROR_CHAT_ID"]
  glucose_increasing_trend_in     = local.envs["GLUCOSE_INCREASING_TREND"]
  device_alerts_bot_token_in      = local.envs["DEVICE_ALERTS_BOT"]
  glucose_alerts_bot_token_in     = local.envs["GLUCOSE_ALERTS_BOT"]

  depends_on = [module.event_hub,module.azure_database, module.azure_redis_cache]

}

module "azure_databricks" {
  source                  = "./modules/azure_databricks"
  name_in                 = var.databricks_workspace_name
  resource_group_name_in  = module.resource_group.resource_group_name_out
  location_in             = var.location
  sku_in                  = var.sku
  cluster_name_in         = var.cluster_name
  spark_version_in        = var.spark_version
  node_type_id_in         = var.node_type
  cluster_term_minutes_in = var.cluster_termination_minutes
  num_workers_in          = var.num_workers
  schedule_task_in        = var.scheduling_quartz_expression
  schedule_timezone_in   = var.timezone_id
  storage_account_name_in = module.storage_account.storage_account_name_out
  storage_account_key_in  = module.storage_account.account_key_out
  container_name_in       = module.storage_account.container_name_out
  event_hub_conn_str_in   = module.event_hub.namespace_name_rule_connection_string_out
  redis_host_in           = module.azure_redis_cache.host_name_out
  port_in                 = module.azure_redis_cache.ssl_port_out
  password_in             = module.azure_redis_cache.primary_access_key_out

}
