locals {
  common_labels = {
    app         = var.app_name
    environment = var.environment
  }
}

resource "kubernetes_namespace_v1" "lab_portal" {
  metadata {
    name   = var.namespace
    labels = local.common_labels
  }
}

resource "kubernetes_deployment_v1" "lab_portal" {
  metadata {
    name      = var.app_name
    namespace = kubernetes_namespace_v1.lab_portal.metadata[0].name
    labels    = local.common_labels
  }

  spec {
    replicas = var.replicas

    selector {
      match_labels = {
        app = var.app_name
      }
    }

    template {
      metadata {
        labels = local.common_labels
      }

      spec {
        container {
          name              = var.app_name
          image             = var.image
          image_pull_policy = var.image_pull_policy

          port {
            container_port = var.container_port
          }

          resources {
            requests = {
              cpu    = var.cpu_request
              memory = var.memory_request
            }

            limits = {
              cpu    = var.cpu_limit
              memory = var.memory_limit
            }
          }

          liveness_probe {
            http_get {
              path = var.liveness_path
              port = var.container_port
            }

            initial_delay_seconds = var.liveness_initial_delay_seconds
            period_seconds        = 10
          }

          readiness_probe {
            http_get {
              path = var.readiness_path
              port = var.container_port
            }

            initial_delay_seconds = var.readiness_initial_delay_seconds
            period_seconds        = 5
          }
        }
      }
    }
  }
}