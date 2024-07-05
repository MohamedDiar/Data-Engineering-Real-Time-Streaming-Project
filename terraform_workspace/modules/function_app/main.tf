#-------modules/function_app/main.tf-------

#Creating service plan
resource "azurerm_service_plan" "iot_stream_service_plan" {
  name                = var.service_plan_name_in
  location            = var.location_in
  resource_group_name = var.resource_group_name_in
  os_type             = var.os_type_in
  sku_name            = var.sku_name_in
}

#Creating function app
resource "azurerm_linux_function_app" "iot_stream_DatabaseInserts_function_app" {
  name                       = "DatabaseInsertFunctionApp"
  location                   = var.location_in
  resource_group_name        = var.resource_group_name_in
  service_plan_id            = azurerm_service_plan.iot_stream_service_plan.id
  storage_account_name       = var.storage_account_name_in
  storage_account_access_key = var.storage_account_access_key_in
  app_settings = {
    "ENABLE_ORYX_BUILD"              = "true"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "FUNCTIONS_WORKER_RUNTIME"       = "python"
    "AzureWebJobsFeatureFlags"       = "EnableWorkerIndexing"
    "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.functionapps_application_insight.instrumentation_key
    "host"                           = var.hostname_in
    "user"                           = var.sql_server_admin_in
    "password"                       = var.sql_server_password_in
    "database"                       = var.sql_database_name_in
    "port"                           = var.port_in
    "EventHubConnectionString"       = var.event_hub_conn_str_in
  }

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  zip_deploy_file = data.archive_file.DatabaseInserts_function.output_path

  depends_on = [data.archive_file.DatabaseInserts_function]

  # Sync function triggers
  provisioner "local-exec" {
    command = "az resource invoke-action --resource-group ${var.resource_group_name_in} --action syncfunctiontriggers --name ${azurerm_linux_function_app.iot_stream_DatabaseInserts_function_app.name} --resource-type Microsoft.Web/sites"
  }

}

resource "azurerm_linux_function_app" "iot_stream_TelegramAlerts_function_app" {
  name                       = "TelegramAlertsFunctionApp"
  location                   = var.location_in
  resource_group_name        = var.resource_group_name_in
  service_plan_id            = azurerm_service_plan.iot_stream_service_plan.id
  storage_account_name       = var.storage_account_name_in
  storage_account_access_key = var.storage_account_access_key_in
  app_settings = {
    "ENABLE_ORYX_BUILD"              = "true"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "FUNCTIONS_WORKER_RUNTIME"       = "python"
    "AzureWebJobsFeatureFlags"       = "EnableWorkerIndexing"
    "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.functionapps_application_insight.instrumentation_key
    "LOW_GLUCOSE_CHAT_ID"            = var.low_glucose_chat_id_in
    "HIGH_GLUCOSE_CHAT_ID"           = var.high_glucose_chat_id_in
    "TRANSMISSION_QUALITY_CHAT_ID"   = var.transmission_quality_chat_id_in
    "DISCONNECTED_ERROR_CHAT_ID"     = var.disconnected_error_chat_id_in
    "GLUCOSE_INCREASING_TREND"       = var.glucose_increasing_trend_in
    "GLUCOSE_ALERTS_BOT"             = var.glucose_alerts_bot_token_in
    "DEVICE_ALERTS_BOT"              = var.device_alerts_bot_token_in
    "EventHubConnectionString"       = var.event_hub_conn_str_in
  }

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  zip_deploy_file = data.archive_file.TelegramAlerts_function.output_path

  depends_on = [data.archive_file.TelegramAlerts_function]

  # Sync function triggers
  provisioner "local-exec" {
    command = "az resource invoke-action --resource-group ${var.resource_group_name_in} --action syncfunctiontriggers --name ${azurerm_linux_function_app.iot_stream_TelegramAlerts_function_app.name} --resource-type Microsoft.Web/sites"
  }

}

# #Creating function app
resource "azurerm_linux_function_app" "iot_stream_ETLDuckdb_function_app" {
  name                       = "ETLDuckdbFunctionApp"
  location                   = var.location_in
  resource_group_name        = var.resource_group_name_in
  service_plan_id            = azurerm_service_plan.iot_stream_service_plan.id
  storage_account_name       = var.storage_account_name_in
  storage_account_access_key = var.storage_account_access_key_in
  app_settings = {
    "ENABLE_ORYX_BUILD"              = "true"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "FUNCTIONS_WORKER_RUNTIME"       = "python"
    "AzureWebJobsFeatureFlags"       = "EnableWorkerIndexing"
    "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.functionapps_application_insight.instrumentation_key
    "account_key"                    = var.storage_account_access_key_in
    "account_name"                   = var.storage_account_name_in
    "host"                           = var.hostname_in
    "user"                           = var.sql_server_admin_in
    "password"                       = var.sql_server_password_in
    "port"                           = var.port_in
    "database"                       = var.sql_database_name_in
    "SCHEDULE_ETL"                   = var.schedule_expressions_in.schedule_info_etl
    "SCHEDULE_FACT_INSERT"           = var.schedule_expressions_in.schedule_info_fact
  }

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  zip_deploy_file = data.archive_file.ETLDuckdb_function.output_path

  depends_on = [data.archive_file.ETLDuckdb_function]

  # Sync function triggers
  provisioner "local-exec" {
    command = "az resource invoke-action --resource-group ${var.resource_group_name_in} --action syncfunctiontriggers --name ${azurerm_linux_function_app.iot_stream_ETLDuckdb_function_app.name} --resource-type Microsoft.Web/sites"
  }

}

resource "azurerm_application_insights" "functionapps_application_insight" {
  name                = "FunctionAppsInsight"
  resource_group_name = var.resource_group_name_in
  location            = var.location_in
  application_type    = "other"
}


resource "azurerm_linux_function_app" "iot_stream_cache_update_function_app" {
  name                       = "CacheUpdateAppFunction"
  location                   = var.location_in
  resource_group_name        = var.resource_group_name_in
  service_plan_id            = azurerm_service_plan.iot_stream_service_plan.id
  storage_account_name       = var.storage_account_name_in
  storage_account_access_key = var.storage_account_access_key_in
  app_settings = {
    "ENABLE_ORYX_BUILD"              = "true"
    "SCM_DO_BUILD_DURING_DEPLOYMENT" = "true"
    "FUNCTIONS_WORKER_RUNTIME"       = "python"
    "AzureWebJobsFeatureFlags"       = "EnableWorkerIndexing"
    "APPINSIGHTS_INSTRUMENTATIONKEY" = azurerm_application_insights.functionapps_application_insight.instrumentation_key
    "host"                           = var.hostname_in
    "user"                           = var.sql_server_admin_in
    "password"                       = var.sql_server_password_in
    "database"                       = var.sql_database_name_in
    "port"                           = var.port_in
    "EventHubConnectionString"       = var.event_hub_conn_str_in
    "REDIS_HOST_NAME"                = var.redis_host_in
    "REDIS_SSL_PORT"                 = var.redis_port_in
    "REDIS_PRIMARY_ACCESS_KEY"       = var.redis_password_in
  }

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  zip_deploy_file = data.archive_file.CacheUpdate_function.output_path

  depends_on = [data.archive_file.CacheUpdate_function]

  # Sync function triggers
  provisioner "local-exec" {
    command = "az resource invoke-action --resource-group ${var.resource_group_name_in} --action syncfunctiontriggers --name ${azurerm_linux_function_app.iot_stream_cache_update_function_app.name} --resource-type Microsoft.Web/sites"
  }
}


data "archive_file" "DatabaseInserts_function" {
  type        = "zip"
  excludes    = split("\n", file("${path.root}/../Azure Functions/DatabaseInserts/.funcignore"))
  source_dir  = "${path.root}/../Azure Functions/DatabaseInserts"
  output_path = "${path.root}/../DatabaseInserts.zip"
  depends_on  = []
}

data "archive_file" "TelegramAlerts_function" {
  type        = "zip"
  excludes    = split("\n", file("${path.root}/../Azure Functions/TelegramAlerts/.funcignore"))
  source_dir  = "${path.root}/../Azure Functions/TelegramAlerts"
  output_path = "${path.root}/../TelegramAlerts.zip"
}

data "archive_file" "ETLDuckdb_function" {
  type        = "zip"
  excludes    = split("\n", file("${path.root}/../Azure Functions/ETLDuckdb/.funcignore"))
  source_dir  = "${path.root}/../Azure Functions/ETLDuckdb"
  output_path = "${path.root}/../ETLDuckdb.zip"
}

data "archive_file" "CacheUpdate_function" {
  type        = "zip"
  excludes    = split("\n", file("${path.root}/../Azure Functions/CacheUpdate/.funcignore"))
  source_dir  = "${path.root}/../Azure Functions/CacheUpdate"
  output_path = "${path.root}/../CacheUpdate.zip"
}