terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
  }
  backend "gcs" {
    bucket = "traceit-2026-tfstate"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "topic_id" {
  type    = string
  default = "device-locations"
}

variable "notification_channels" {
  type    = list(string)
  default = []
}

variable "database_url" {
  type      = string
  sensitive = true
}

variable "cloud_run_service_name" {
  type    = string
  default = "traceit-dev"
}

# Pub/Sub Topic
resource "google_pubsub_topic" "device_locations" {
  name = var.topic_id
}

# Pub/Sub Subscription
resource "google_pubsub_subscription" "device_locations_sub" {
  name  = "${var.topic_id}-sub"
  topic = google_pubsub_topic.device_locations.id
  ack_deadline_seconds = 20
}

# Cloud Run Service
resource "google_cloud_run_service" "traceit" {
  name     = var.cloud_run_service_name
  location = var.region

  template {
    spec {
      containers {
        image = "us.gcr.io/${var.project_id}/traceit:v1"
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
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access to Cloud Run
resource "google_cloud_run_service_iam_member" "invoker" {
  service  = google_cloud_run_service.traceit.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Local to extract hostname from Cloud Run URL
locals {
  cloud_run_host = replace(google_cloud_run_service.traceit.status[0].url, "https://", "")
}

# Uptime check for Cloud Run service
resource "google_monitoring_uptime_check_config" "api_uptime" {
  display_name = "traceit-api-uptime"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path           = "/docs"
    port           = 443
    request_method = "GET"
    use_ssl        = true
    validate_ssl   = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = local.cloud_run_host
    }
  }
}

# Alerting policy: alert when uptime check fails for 1 minute
resource "google_monitoring_alert_policy" "uptime_alert" {
  display_name = "TraceIt API Uptime Alert"
  combiner     = "OR"

  conditions {
    display_name = "Uptime check failed"
    condition_threshold {
      filter          = "resource.type = \"uptime_url\" AND metric.type = \"monitoring.googleapis.com/uptime_check/check_passed\""
      duration        = "60s"
      comparison      = "COMPARISON_LT"
      threshold_value = 1
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_FRACTION_TRUE"
      }
    }
  }

  notification_channels = var.notification_channels

  alert_strategy {
    auto_close = "604800s"
  }
}
