#-------/modules/azure_networking/output.tf-------

output "network_interface_id_out" {
  description = "The IDs of the network interfaces."
  value       = azurerm_network_interface.stream_nic.id
}