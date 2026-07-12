output "bucket_name" {
  value = google_storage_bucket.data_lake.name
}

output "service_account_email" {
  value = google_service_account.pipeline_sa.email
}