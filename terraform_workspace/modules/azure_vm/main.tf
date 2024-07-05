#-------/modules/azure_vm/main.tf-------

resource "tls_private_key" "vm_ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "azurerm_linux_virtual_machine" "stream_debezium_vm" {
  name                  = var.vm_name_in
  resource_group_name   = var.resource_group_name_in
  location              = var.location_in
  size                  = var.vm_size_in
  admin_username        = var.admin_username_in
  network_interface_ids = [var.network_interface_id_in]

  admin_ssh_key {
    username   = var.admin_username_in
    public_key = tls_private_key.vm_ssh_key.public_key_openssh
  }

  provisioner "local-exec" {
    command = <<EOT
    mkdir -p ~/.ssh
    echo '${tls_private_key.vm_ssh_key.private_key_pem}' > ~/.ssh/${var.ssh_key_name_in}.pem
    chmod 600 ~/.ssh/${var.ssh_key_name_in}.pem
  EOT
  }
  os_disk {
    caching              = var.os_disk_configs_in.caching
    storage_account_type = var.os_disk_configs_in.storage_account_type
    disk_size_gb         = var.os_disk_configs_in.disk_size_gb
  }

  source_image_reference {
    publisher = var.vm_image_configs_in.publisher
    offer     = var.vm_image_configs_in.offer
    sku       = var.vm_image_configs_in.sku
    version   = var.vm_image_configs_in.version
  }
}

#Bootstrap the VM to automatically install and start the Debezium Server
resource "azurerm_virtual_machine_extension" "vmext" {
  name                 = "debezium_server_setup"
  virtual_machine_id   = azurerm_linux_virtual_machine.stream_debezium_vm.id
  publisher            = "Microsoft.Azure.Extensions"
  type                 = "CustomScript"
  type_handler_version = "2.0"

  protected_settings = <<PROT
  {
    "script": "${base64encode(templatefile("${path.module}/debezium_setup.sh", { username = "${var.admin_username_in}",
  hostname     = "${var.hostname_in}",
  db_port      = "${var.port_in}", db_name = "${var.sql_database_name_in}", db_username = "${var.sql_server_admin_in}",
  db_password  = "${var.sql_server_password_in}", event_hub_conn_str = "${var.event_hub_conn_str_in}",
  file_content = "${file("${path.module}/local_application.properties")}"
}))}"
  }
  PROT
#   depends_on = [ azurerm_linux_virtual_machine.stream_debezium_vm ]
}


resource "null_resource" "write_ssh_command" {

  depends_on = [azurerm_linux_virtual_machine.stream_debezium_vm]
  provisioner "local-exec" {
    command = <<EOT
    echo "" >> "${path.root}/../.env"
    echo "#-----------Azure VM SSH Connection Info---------#" >> "${path.root}/../.env"
    echo "SSH_USER='${var.admin_username_in}'" >> "${path.root}/../.env"
    echo "SSH_HOST='${azurerm_linux_virtual_machine.stream_debezium_vm.public_ip_address}'" >> "${path.root}/../.env"
    echo "SSH_KEY_PATH='~/.ssh/${var.ssh_key_name_in}.pem'" >> "${path.root}/../.env"
  EOT
  }
}


