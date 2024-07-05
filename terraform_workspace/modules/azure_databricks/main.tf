#------modules/azure_databricks/main.tf------

resource "azurerm_databricks_workspace" "iot_glucose_streaming_workspace" {
  name                = var.name_in
  resource_group_name = var.resource_group_name_in
  location            = var.location_in
  sku                 = var.sku_in

}


resource "databricks_cluster" "spark_streaming_cluster" {
  cluster_name  = var.cluster_name_in.cluster_name_streaming
  spark_version = var.spark_version_in
  node_type_id  = var.node_type_id_in

  autotermination_minutes = var.cluster_term_minutes_in #If no activity is detected for 10 minutes, the cluster will automatically terminate
  num_workers             = var.num_workers_in

  spark_conf = {
    # Single-node
    "spark.databricks.cluster.profile" : "singleNode"
    "spark.master" : "local[*, 4]"
  }

  custom_tags = {
    "ResourceClass" = "SingleNode"
  }

  spark_env_vars = {
    "PYSPARK_PYTHON"           = "/databricks/python3/bin/python3"
    "EVENT_HUB_CONNECTION_STR" = var.event_hub_conn_str_in
    "REDIS_HOST_NAME"          = var.redis_host_in
    "REDIS_SSL_PORT"           = var.port_in
    "REDIS_PRIMARY_ACCESS_KEY" = var.password_in
  }

  library {
    maven {
      coordinates = "com.microsoft.azure:azure-eventhubs-spark_2.12:2.3.17"
    }
  }

  library {
    pypi {
      package = "redis==5.0.4"

    }
  }
  depends_on = [azurerm_databricks_workspace.iot_glucose_streaming_workspace]
}

resource "null_resource" "wait_for_workspace" {
  provisioner "local-exec" {
    command = "sleep 120"  # Wait for 2 minutes to ensure workspace is active
  }

  depends_on = [azurerm_databricks_workspace.iot_glucose_streaming_workspace]
}


#Shcedule the job to run at 5:00 AM on the first day of every month
resource "databricks_job" "spark_batch_trend_analysis" {
  name = "Spark Batch Trend Analysis"

  job_cluster {
    job_cluster_key = "j"
    new_cluster {
      spark_version = var.spark_version_in
      node_type_id  = var.node_type_id_in
      num_workers   = var.num_workers_in

      #IF single node, spark.databricks.cluster.profile should be set to singleNode ad custom tags is needed as well,
      spark_conf = {
        # Single-node
        "spark.databricks.cluster.profile" : "singleNode"
        "spark.master" : "local[*, 4]"
      }

      custom_tags = {
        "ResourceClass" = "SingleNode"
      }

      spark_env_vars = {
        "PYSPARK_PYTHON"           = "/databricks/python3/bin/python3"
        "EVENT_HUB_CONNECTION_STR" = var.event_hub_conn_str_in
        "account_name"             = var.storage_account_name_in
        "account_key"              = var.storage_account_key_in
        "container_name"           = var.container_name_in
      }


    }

  }


  task {
    task_key        = "a"
    job_cluster_key = "j"
    max_retries     = 5

    notebook_task {
      notebook_path = databricks_notebook.spark_glucose_batch.path
    }

    library {
      maven {
        coordinates = "com.microsoft.azure:azure-eventhubs-spark_2.12:2.3.17"
      }
    }

  }
  #Default expression passed in Runs the job at 5:00 AM on the first day of every month
  schedule {
    quartz_cron_expression = var.schedule_task_in
    timezone_id            = var.schedule_timezone_in
  }


  depends_on = [null_resource.wait_for_workspace]
  # depends_on = [databricks_notebook.spark_glucose_batch]

  


}

resource "databricks_notebook" "spark_glucose_streaming" {
  source = "${path.root}/../Azure Databricks Notebooks/Glucose Monitoring Streaming Business Logic.dbc"
  path   = "/Shared/Glucose Monitoring Streaming Business Logic"

  lifecycle {
    ignore_changes = [
      format,
      language,
    ]
  }
}

resource "databricks_notebook" "spark_glucose_batch" {
  source = "${path.root}/../Azure Databricks Notebooks/Trend Analysis.dbc"
  path   = "/Shared/Trend Analysis"

  lifecycle {
    ignore_changes = [
      format,
      language,
    ]
  }
  # depends_on = [azurerm_databricks_workspace.iot_glucose_streaming_workspace]
}
