resource "kubernetes_service_v1" "lab_portal" {
  metadata {
    name      = "${var.app_name}-service"
    namespace = kubernetes_namespace_v1.lab_portal.metadata[0].name
    labels    = local.common_labels
  }

  spec {
    type = var.service_type

    selector = {
      app = var.app_name
    }

    port {
      name        = "http"
      protocol    = "TCP"
      port        = var.service_port
      target_port = var.container_port
      node_port   = var.service_type == "NodePort" ? var.node_port : null
    }
  }
}