#------root/variables.tf------



#---------- RESOURCE GROUP VARIABLES ------------
variable "resource_name" {
  description = "The name of the resource group in which the resources will be created."
  default     = "Glucose_Continous_Monitoring_Streaming_Project"
}

variable "location" {
  type        = string
  description = "The location in which the resources will be created."
  default     = "Central US"
}

#---------- STORAGE ACCOUNT VARIABLES ------------

variable "storage_account_name" {
  description = "The name of the storage account."
  default     = "glucosemonitoring"
}

variable "account_tier" {
  type        = string
  description = "The tier of the storage account."
  default     = "Standard"
}


variable "account_replication_type" {
  type        = string
  description = "The replication type of the storage account."
  default     = "GRS"
}

#---------- SQL SERVER VARIABLES ------------
variable "sql_server_name" {
  description = "The name of the SQL server."
  default     = "iotstreamingserver"
}


variable "sql_server_backup_retention_days" {
  type        = number
  description = "The number of days to retain backups for."
  default     = 7

}

variable "sql_server_sku_name" {
  type        = string
  description = "The name of the SKU for the MYSQL server."
  default     = "B_Standard_B1ms"
}

variable "storage_config" {
  type = object({
    auto_growth = bool
    size_gb     = number
    iops        = number
  })
  description = "The storage configuration for the SQL server."
  default = {
    auto_growth = false
    size_gb     = 25
    iops        = 375


  }
}

variable "MYSQL_port" {
  type        = number
  description = "The port number of the SQL server."
  default     = 3306

}

variable "server_configs" {
  description = "This config map contains the configuration for the SQL server."
  type = map(object({
    name  = string
    value = string
  }))
  default = {
    "binlog_expire_logs_seconds" = {
      name  = "binlog_expire_logs_seconds"
      value = "86400"
    }
    "binlog_row_image" = {
      name  = "binlog_row_image"
      value = "FULL"
    }
  }
}


#---------- SQL DATABASE VARIABLES ------------
variable "sql_database_name" {
  description = "The name of the SQL database."
  default     = "iotstreamdb"

  validation {
    condition     = can(regex("^[^<>\\/%&*:.' ]+$", var.sql_database_name)) && !endswith(var.sql_database_name, ". ")
    error_message = "Invalid database name. It cannot end with '.' or ' ' and cannot contain '<,>,*,%,&,:,\\,/,?' or control characters."
  }
}

variable "sql_database_collation" {
  type        = string
  description = "The collation of the SQL database."
  default     = "utf8_unicode_ci"

}

#---------- EVENT HUBs VARIABLES -------------

#---------Event Hub Namespace Variables--------
variable "ev_sku_name" {
  type        = string
  description = "The name of the SKU for the Event Hub namespace."
  default     = "Standard"
}

variable "ev_capacity" {
  type        = number
  description = "The capacity of the Event Hub namespace."
  default     = 1
}

variable "auto_inflate_enabled" {
  type        = bool
  description = "Indicates whether Auto Inflate is enabled for the Event Hub namespace."
  default     = true
}

variable "max_throughput_units" {
  type        = number
  description = "The maximum number of throughput units for the Event Hub namespace in case auto-inflate is enabled."
  default     = 3
}
#---------Event Hub Variables--------
variable "event_hub_names" {
  type        = list(any)
  description = "The names of the Event Hubs to create."
  default     = ["raw_glucose_readings", "raw_device_feeds", "above_max_glucose_threshold", "below_min_glucose_threshold", "missed_readings", "device_error", "increasing_trend_alert", "cache_update"]
}

variable "event_hub_configs" {
  description = "This config map contains the configuration for each Event Hub."
  type = map(object({
    partition_count   = number
    message_retention = number
    consumer_groups   = list(any)
  }))
  default = {
    raw_glucose_readings = {
      partition_count   = 1
      message_retention = 1
      consumer_groups   = ["mysql_glucose_reading_table", "spark", "streamlit"]
    }
    raw_device_feeds = {
      partition_count   = 1
      message_retention = 1
      consumer_groups   = ["mysql_device_feed_table", "spark"]
    }
    above_max_glucose_threshold = {
      partition_count   = 1
      message_retention = 1
      consumer_groups   = ["telegrambot"]
    }
    below_min_glucose_threshold = {
      partition_count   = 1
      message_retention = 1
      consumer_groups   = ["below_min"]
    }
    missed_readings = {
      partition_count   = 1
      message_retention = 1
      consumer_groups   = ["transmission_quality"]
    }
    device_error = {
      partition_count   = 1
      message_retention = 1
      consumer_groups   = ["lost_connection"]
    }
    increasing_trend_alert = {
      partition_count   = 1
      message_retention = 1
      consumer_groups   = ["sparksql"]
    }
    cache_update = {
      partition_count   = 1
      message_retention = 1
      consumer_groups   = ["redis_cache"]
    }
  }
}

#----------AZURE NETWORKING VARIABLES------------

variable "vnet_configs" {
  description = "This config map contains the configuration for the virtual network."
  type = object({
    name          = string
    address_space = list(string)
  })
  default = {
    name = "iotstreamvnet"
  address_space = ["10.0.0.0/16"] }
}

variable "subnet_configs" {
  description = "This config map contains the configuration for the subnet."
  type = object({
    name             = string
    address_prefixes = list(string)
  })
  default = {
    name             = "iotstreamsubnet"
    address_prefixes = ["10.0.0.0/24"]
  }
}

variable "nic_configs" {
  description = "This config map contains the configuration for the network interface."
  type = object({
    name = string
    ip_configuration = object({
      name                          = string
      private_ip_address_allocation = string
    })
  })
  default = {
    name = "iotstreamnic"
    ip_configuration = {
      name                          = "iotstreamipconfig"
      private_ip_address_allocation = "Dynamic"
    }
  }
}

variable "security_group_name" {
  description = "The name of the network security group."
  default     = "iotstreamnsg"
}
#---------- AZURE VIRUTAL MACHINE VARIABLES ------------
variable "vm_name" {
  description = "The name of the virtual machine."
  default     = "debeziumservervm"
}

variable "vm_size" {
  type        = string
  description = "The size of the virtual machine."
  default     = "Standard_B2s"
}

variable "admin_username" {
  description = "The administrator username for the virtual machine."
  default     = "adminuser"
}


variable "os_disk_configs" {
  description = "This config map contains the configuration for the OS disk of the virtual machine."
  type = object({
    storage_account_type = string
    caching              = string
    disk_size_gb         = number
  })
  default = {
    storage_account_type = "StandardSSD_LRS"
    caching              = "ReadWrite"
    disk_size_gb         = 30
  }
}

variable "source_image_configs" {
  description = "This config map contains the configuration for the source image of the virtual machine."
  type = object({
    publisher = string
    offer     = string
    sku       = string
    version   = string
  })
  default = {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "20.04.202209200"

  }

}

variable "ssh_key_name" {
  description = "The name of the SSH key."
  default     = "vmKey"

}

#---------- FUNCTION APP VARIABLES ------------
variable "service_plan_name" {
  description = "The name of the service plan."
  default     = "iotstreamingserviceplan"
}

variable "os_type" {
  type        = string
  description = "The operating system type of the service plan."
  default     = "Linux"
}

variable "sku_name" {
  type        = string
  description = "The name of the SKU for the service plan."
  default     = "Y1"
}
# Reads as 2:00 AM for schedule_info_etl and 2:30 AM for schedule_info_fact
variable "schedule_expressions" {
  description = "This config map contains the schedule expressions for the two functions in ETLDuckdb Function App."
  type = object({
    schedule_info_etl  = string
    schedule_info_fact = string
  })
  default = {
    schedule_info_etl  = "0 00 02 * * *"
    schedule_info_fact = "0 30 02 * * *"
  }
}


#---------- REDIS CACHE VARIABLES ------------
variable "cache_name" {
  description = "The name of the Redis cache. It has to be globally unique."
  default     = "iotstreamcache"
}

variable "cache_capacity" {
  type        = number
  description = "The size of the Redis cache to deploy. Valid SKU values for Basic/Standard go up to 6. Valid SKU values for Premium go up to 5."
  default     = 0
}

variable "cache_family" {
  type        = string
  description = "The SKU family/pricing group to use. Valid values are C (for Basic/Standard SKU family) and P (for Premium)"
  default     = "C"
}

variable "cache_sku_name" {
  type        = string
  description = "The name of the SKU for the Redis cache."
  default     = "Basic"
}

#---------- AZURE DATABRICKS VARIABLES ------------
variable "databricks_workspace_name" {
  description = "The name of the Azure Databricks workspace."
  default     = "iotstreamdatabricks"
}

variable "sku" {
  type        = string
  description = "The SKU of the Azure Databricks workspace."
  default     = "standard"
}


variable "cluster_name" {
  type = object({
    cluster_name_streaming = string
    cluster_name_batch     = string
  })
  description = "The name of the cluster to create."
  default = {
    cluster_name_streaming = "spark_streaming_cluster"
    cluster_name_batch     = "spark_batch_cluster"
  }
}

variable "spark_version" {
  type        = string
  description = "The version of Spark to use."
  default     = "13.3.x-scala2.12"
}

variable "node_type" {
  type        = string
  description = "The type of node to use."
  default     = "Standard_DS3_v2"

}

variable "cluster_termination_minutes" {
  type        = number
  description = "The number of minutes of inactivity before the cluster is terminated."
  default     = 10
}

variable "num_workers" {
  type        = number
  description = "The number of workers to use."
  default     = 0
}

variable "scheduling_quartz_expression" {
  type        = string
  description = "The Quartz expression to use for scheduling the job."
  #Defaul is Runs the job at 5:00 AM on the first day of every month
  default = "0 0 5 1 * ? *"

}
variable "timezone_id" {
  type        = string
  description = "The timezone to use for the schedule."
  default     = "Europe/Madrid"
  
}
#----------OTHERS-----------

locals {
  envs = { for tuple in regexall("(.*?)=(.*)", file("../.env")) : tuple[0] => tuple[1] }
}


