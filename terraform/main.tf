terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "data_lake" {
  name          = var.bucket_name
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_bigquery_dataset" "raw" {
  dataset_id = "raw"
  project    = var.project_id
  location   = var.region
}

resource "google_bigquery_dataset" "staging" {
  dataset_id = "staging"
  project    = var.project_id
  location   = var.region
}

resource "google_bigquery_dataset" "marts" {
  dataset_id = "marts"
  project    = var.project_id
  location   = var.region
}

resource "google_service_account" "pipeline_sa" {
  account_id   = "pet-food-pipeline"
  display_name = "Pet Food Pipeline Service Account"
}

resource "google_project_iam_member" "pipeline_sa_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_project_iam_member" "pipeline_sa_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_project_iam_member" "pipeline_sa_bigquery_job" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}