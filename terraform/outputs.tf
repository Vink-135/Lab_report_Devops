output "namespace" {
  description = "Namespace created for the application."
  value       = kubernetes_namespace_v1.lab_portal.metadata[0].name
}

output "deployment_name" {
  description = "Name of the Kubernetes deployment."
  value       = kubernetes_deployment_v1.lab_portal.metadata[0].name
}

output "service_name" {
  description = "Name of the Kubernetes service."
  value       = kubernetes_service_v1.lab_portal.metadata[0].name
}

output "service_type" {
  description = "Kubernetes service type."
  value       = kubernetes_service_v1.lab_portal.spec[0].type
}

output "node_port" {
  description = "Allocated NodePort when the service type is NodePort."
  value       = var.service_type == "NodePort" ? var.node_port : null
}