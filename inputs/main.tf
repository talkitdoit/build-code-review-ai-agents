terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "3.29.1" # testing with the latest (major) version of the AzureRM Provider
    }
    tls = {
      source = "hashicorp/tls"
    }
  }
}

provider "azurerm" {
  features {}
}

locals {
  storage_account_prefix = "aiagent"
}

data "azurerm_client_config" "current" {
}

resource "random_string" "prefix" {
  length  = 6
  special = false
  upper   = false
  numeric = false
}

resource "random_string" "storage_account_suffix" {
  length  = 8
  special = false
  lower   = true
  upper   = false
  numeric  = false
}

resource "azurerm_resource_group" "rg" {
  name     = var.name_prefix == null ? "${random_string.prefix.result}${var.resource_group_name}" : "${var.name_prefix}${var.resource_group_name}"
  location = var.location
  tags     = var.tags
}

module "virtual_network" {
  source                       = "./modules/virtual_network"
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = var.location
  vnet_name                    = var.name_prefix == null ? "${random_string.prefix.result}${var.vnet_name}" : "${var.name_prefix}${var.vnet_name}"
  address_space                = var.vnet_address_space
  tags                         = var.tags

  subnets = [
    {
      name : var.system_node_pool_subnet_name
      address_prefixes : var.system_node_pool_subnet_address_prefix
      private_endpoint_network_policies_enabled : false
      private_link_service_network_policies_enabled : false
      delegation: null
    },
    {
      name : var.user_node_pool_subnet_name
      address_prefixes : var.user_node_pool_subnet_address_prefix
      private_endpoint_network_policies_enabled : false
      private_link_service_network_policies_enabled : false
      delegation: null
    },
    {
      name : var.pod_subnet_name
      address_prefixes : var.pod_subnet_address_prefix
      private_endpoint_network_policies_enabled : false
      private_link_service_network_policies_enabled : false
      # delegation: "Microsoft.ContainerService/managedClusters"
      delegation: null
    },
    {
      name : var.vm_subnet_name
      address_prefixes : var.vm_subnet_address_prefix
      private_endpoint_network_policies_enabled : false
      private_link_service_network_policies_enabled : false
      delegation: null
    },
    {
      name : "AzureBastionSubnet"
      address_prefixes : var.bastion_subnet_address_prefix
      private_endpoint_network_policies_enabled : false
      private_link_service_network_policies_enabled : false
      delegation: null
    }
  ]
}

module "storage_account" {
  source                      = "./modules/storage_account"
  name                        = "${local.storage_account_prefix}${random_string.storage_account_suffix.result}"
  location                    = var.location
  resource_group_name         = azurerm_resource_group.rg.name
  account_kind                = var.storage_account_kind
  account_tier                = var.storage_account_tier
  replication_type            = var.storage_account_replication_type
  tags                        = var.tags

}

module "bastion_host" {
  source                       = "./modules/bastion_host"
  name                         = var.name_prefix == null ? "${random_string.prefix.result}${var.bastion_host_name}" : "${var.name_prefix}${var.bastion_host_name}"
  location                     = var.location
  resource_group_name          = azurerm_resource_group.rg.name
  subnet_id                    = module.virtual_network.subnet_ids["AzureBastionSubnet"]
  tags                         = var.tags
}

module "virtual_machine" {
  count                               = var.vm_enabled ? 1 : 0
  source                              = "./modules/virtual_machine"
  name                                = var.name_prefix == null ? "${random_string.prefix.result}${var.vm_name}" : "${var.name_prefix}${var.vm_name}"
  size                                = var.vm_size
  location                            = var.location
  public_ip                           = var.vm_public_ip
  vm_user                             = var.admin_username
  # admin_ssh_public_key                = var.ssh_public_key
  # admin_ssh_public_key                = var.ssh_public_key
  os_disk_image                       = var.vm_os_disk_image
  resource_group_name                 = azurerm_resource_group.rg.name
  subnet_id                           = module.virtual_network.subnet_ids[var.vm_subnet_name]
  os_disk_storage_account_type        = var.vm_os_disk_storage_account_type
  tags                                = var.tags
  key_vault_id = module.key_vault.id
}

module "key_vault" {
  source                          = "./modules/key_vault"
  name                            = var.name_prefix == null ? "${random_string.prefix.result}${var.key_vault_name}" : "${var.name_prefix}${var.key_vault_name}"
  location                        = var.location
  resource_group_name             = azurerm_resource_group.rg.name
  tenant_id                       = data.azurerm_client_config.current.tenant_id
  sku_name                        = var.key_vault_sku_name
  enabled_for_deployment          = var.key_vault_enabled_for_deployment
  enabled_for_disk_encryption     = var.key_vault_enabled_for_disk_encryption
  enabled_for_template_deployment = var.key_vault_enabled_for_template_deployment
  enable_rbac_authorization       = var.key_vault_enable_rbac_authorization
  purge_protection_enabled        = var.key_vault_purge_protection_enabled
  soft_delete_retention_days      = var.key_vault_soft_delete_retention_days
  bypass                          = var.key_vault_bypass
  default_action                  = var.key_vault_default_action
  tags                            = var.tags

  depends_on = [ module.virtual_machine[0].private_ssh_key ]
  # depends_on = [ module.virtual_machine[0].azurerm_key_vault_secret_private_ssh_key ]
}
