terraform {
  required_version = ">= 1.6.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" { type = string }
variable "region" { type = string  default = "us-central1" }
variable "topic_id" { type = string  default = "device-locations" }
variable "notification_channels" { type = list(string) default = [] }

resource "google_pubsub_topic" "device_locations" {
  name = var.topic_id
}

resource "google_pubsub_subscription" "device_locations_sub" {
  name  = "${var.topic_id}-sub"
  topic = google_pubsub_topic.device_locations.id
  ack_deadline_seconds = 20
}

# Basic uptime check for Cloud Run service and alerting policy
resource "google_monitoring_uptime_check_config" "api_uptime" {
  display_name = "traceit-api-uptime"
  http_check {
    path = "/docs"
    port = 443
    request_method = "GET"
    use_ssl = true
    validate_ssl = true
  }
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = google_cloud_run_service.traceit.status[0].url
    }
  }
}

resource "google_cloud_run_service" "traceit" {
  name     = "traceit"
  location = var.region

  template {
    spec {
      containers {
        image = "us.gcr.io/${var.project_id}/traceit:latest"
        env {
          name  = "DATABASE_URL"
          value = var.database_url
        }
        env {
          name  = "ECHO_SQL"
          value = "True"
        }
        env {
          name  = "PUBSUB_ENABLED"
          value = "true"
        }
        env {
          name  = "GCP_PROJECT"
          value = var.project_id
        }
        env {
          name  = "PUBSUB_TOPIC_ID"
          value = var.topic_id
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

resource "google_cloud_run_service_iam_member" "invoker" {
  service  = google_cloud_run_service.traceit.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

variable "database_url" {
  type = string
}

# Alerting policy: alert when uptime check fails for 1 minute
resource "google_monitoring_alert_policy" "uptime_alert" {
  display_name = "TraceIt API Uptime Alert"
  combiner     = "OR"

  conditions {
    display_name = "Uptime check failed"
    condition_monitoring_query_language {
      duration = "60s"
      query    = <<EOT
fetch uptime_url
| metric 'monitoring.googleapis.com/uptime_check/check_passed'
| group_by 1m, [value_check_passed_true: true]
| every 1m
| group_by [resource.host], [value_check_passed_true_aggregate: aggregate(value_check_passed_true)]
| condition value_check_passed_true_aggregate < 1
EOT
    }
  }

  notification_channels = var.notification_channels
}
