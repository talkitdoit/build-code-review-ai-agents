locals {
  storage_account_prefix = "talkitdoit"
}

data "azurerm_client_config" "current" {
}

resource "random_string" "prefix" {
  length  = 6
  special = false
  upper   = false
  numeric = false
}

module "bastion_host" {
  source                       = "./modules/bastion_host"
  name                         = var.name_prefix == null ? "${random_string.prefix.result}${var.bastion_host_name}" : "${var.name_prefix}${var.bastion_host_name}"
  location                     = var.location
  resource_group_name          = azurerm_resource_group.rg.name
  subnet_id                    = module.virtual_network.subnet_ids["AzureBastionSubnet"]
  tags                         = var.tags
}
