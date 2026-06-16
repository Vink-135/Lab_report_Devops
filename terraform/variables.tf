variable "kubeconfig_path" {
  description = "Path to the kubeconfig file used by the Kubernetes provider."
  type        = string
  default     = "~/.kube/config"
}

variable "kubeconfig_context" {
  description = "Optional kubeconfig context to target."
  type        = string
  default     = ""
}

variable "namespace" {
  description = "Namespace to create for the application."
  type        = string
  default     = "lab-portal"

  validation {
    condition     = can(regex("^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", var.namespace)) && length(var.namespace) <= 63
    error_message = "The namespace must be a valid Kubernetes DNS label up to 63 characters."
  }
}

variable "app_name" {
  description = "Application name used for resource metadata."
  type        = string
  default     = "lab-portal"
}

variable "environment" {
  description = "Environment label applied to Kubernetes resources."
  type        = string
  default     = "production"
}

variable "image" {
  description = "Container image used by the deployment."
  type        = string
  default     = "lab-portal:latest"
}

variable "image_pull_policy" {
  description = "Kubernetes image pull policy for the container."
  type        = string
  default     = "Never"

  validation {
    condition     = contains(["Always", "IfNotPresent", "Never"], var.image_pull_policy)
    error_message = "image_pull_policy must be Always, IfNotPresent, or Never."
  }
}

variable "replicas" {
  description = "Number of pod replicas to run."
  type        = number
  default     = 2

  validation {
    condition     = var.replicas >= 1
    error_message = "replicas must be at least 1."
  }
}

variable "container_port" {
  description = "Container port exposed by the application."
  type        = number
  default     = 5000

  validation {
    condition     = var.container_port > 0 && var.container_port <= 65535
    error_message = "container_port must be a valid TCP port."
  }
}

variable "service_port" {
  description = "Service port exposed inside the cluster."
  type        = number
  default     = 5000

  validation {
    condition     = var.service_port > 0 && var.service_port <= 65535
    error_message = "service_port must be a valid TCP port."
  }
}

variable "service_type" {
  description = "Kubernetes service type."
  type        = string
  default     = "NodePort"

  validation {
    condition     = contains(["ClusterIP", "NodePort", "LoadBalancer"], var.service_type)
    error_message = "service_type must be ClusterIP, NodePort, or LoadBalancer."
  }
}

variable "node_port" {
  description = "NodePort used when service_type is NodePort."
  type        = number
  default     = 30050

  validation {
    condition     = var.node_port >= 30000 && var.node_port <= 32767
    error_message = "node_port must be within the Kubernetes NodePort range."
  }
}

variable "cpu_request" {
  description = "CPU request for the container."
  type        = string
  default     = "250m"
}

variable "cpu_limit" {
  description = "CPU limit for the container."
  type        = string
  default     = "500m"
}

variable "memory_request" {
  description = "Memory request for the container."
  type        = string
  default     = "128Mi"
}

variable "memory_limit" {
  description = "Memory limit for the container."
  type        = string
  default     = "256Mi"
}

variable "liveness_path" {
  description = "HTTP path used for the liveness probe."
  type        = string
  default     = "/login"
}

variable "readiness_path" {
  description = "HTTP path used for the readiness probe."
  type        = string
  default     = "/login"
}

variable "liveness_initial_delay_seconds" {
  description = "Initial delay before the liveness probe starts."
  type        = number
  default     = 15
}

variable "readiness_initial_delay_seconds" {
  description = "Initial delay before the readiness probe starts."
  type        = number
  default     = 5
}