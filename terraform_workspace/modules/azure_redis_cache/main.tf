#------modules/azure_redis_cache/main.tf------

resource "azurerm_redis_cache" "redis_cache" {
  name                = var.cache_name_in
  resource_group_name = var.resource_group_name_in
  location            = var.location_in
  capacity            = var.capacity_in
  family              = var.family_in
  sku_name            = var.sku_name_in
}


resource "null_resource" "update_env" {
  depends_on = [azurerm_redis_cache.redis_cache]

  provisioner "local-exec" {
    command = <<EOT
    echo "" >> "${path.root}/../.env"
    echo "#-----------Redis Cache---------#" >> "${path.root}/../.env"
    echo "REDIS_HOST_NAME='${azurerm_redis_cache.redis_cache.hostname}'" >> "${path.root}/../.env"
    echo "REDIS_SSL_PORT=${azurerm_redis_cache.redis_cache.ssl_port}" >> "${path.root}/../.env"
    echo "REDIS_PRIMARY_ACCESS_KEY=${azurerm_redis_cache.redis_cache.primary_access_key}" >> "${path.root}/../.env"
    EOT
  }
}