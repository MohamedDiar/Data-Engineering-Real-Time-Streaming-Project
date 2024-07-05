#-------/modules/azure_networking/main.tf-------

resource "azurerm_virtual_network" "stream_virtual_network" {
  name                = var.vnet_configs_in.name
  address_space       = var.vnet_configs_in.address_space
  location            = var.location_in
  resource_group_name = var.resource_group_name_in
}

resource "azurerm_subnet" "stream_subnet" {
  name                 = var.subnet_configs_in.name
  resource_group_name  = var.resource_group_name_in
  virtual_network_name = azurerm_virtual_network.stream_virtual_network.name
  address_prefixes     = var.subnet_configs_in.address_prefixes
}

resource "azurerm_network_security_group" "stream_network_security_group" {
  name                = var.security_group_name_in
  location            = var.location_in
  resource_group_name = var.resource_group_name_in

  security_rule {
    name                       = "ssh_rule"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "https_rule"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_public_ip" "stream_pip" {
  name                = "iot-stream-pip"
  resource_group_name = var.resource_group_name_in
  location            = var.location_in
  allocation_method   = var.nic_configs_in.ip_configuration.private_ip_address_allocation
}

resource "azurerm_network_interface" "stream_nic" {
  name                = var.nic_configs_in.name
  location            = var.location_in
  resource_group_name = var.resource_group_name_in

  ip_configuration {
    name                          = var.nic_configs_in.ip_configuration.name
    subnet_id                     = azurerm_subnet.stream_subnet.id
    private_ip_address_allocation = var.nic_configs_in.ip_configuration.private_ip_address_allocation
    public_ip_address_id          = azurerm_public_ip.stream_pip.id
  }
}

resource "azurerm_network_interface_security_group_association" "stream_nic_nsg_association" {
  network_interface_id      = azurerm_network_interface.stream_nic.id
  network_security_group_id = azurerm_network_security_group.stream_network_security_group.id
}

