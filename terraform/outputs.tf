output "service_url" {
  value = google_cloud_run_service.traceit.status[0].url
}
