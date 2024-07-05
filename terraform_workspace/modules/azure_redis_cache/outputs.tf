#------modules/azure_redis_cache/output.tf------

output "host_name_out" {
  value = azurerm_redis_cache.redis_cache.hostname

}

output "ssl_port_out" {
  value = azurerm_redis_cache.redis_cache.ssl_port
}

output "primary_access_key_out" {
  value = azurerm_redis_cache.redis_cache.primary_access_key
}

