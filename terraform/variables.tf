variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "asia-southeast1"
}

variable "bucket_name" {
  description = "Name for the GCS data lake bucket"
  type        = string
}