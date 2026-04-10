variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
  default     = "effc09a2-5c94-4ef7-87aa-17b1e00ad454"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
  default     = "finance-tracker-rg"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "finance-tracker"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "kubernetes_version" {
  description = "Kubernetes version for AKS cluster"
  type        = string
  default     = "1.31"
}

variable "node_count" {
  description = "Number of nodes in AKS node pool"
  type        = number
  default     = 2
}

variable "node_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_DC2s_v3"
}
