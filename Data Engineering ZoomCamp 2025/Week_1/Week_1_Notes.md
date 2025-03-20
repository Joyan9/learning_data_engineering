# Week 1 Notes

## Introduction to Docker
Docker is a platform that allows you to package applications along with their dependencies into standardized units called containers.

In data engineering, Docker provides consistent environments for running data pipelines regardless of the underlying infrastructure.

### Why Docker (Data Engineering Focus)
1. **Reproducibility**: Creates consistent environments for data pipelines across development, testing, and production
2. **Isolation**: Packages all dependencies together to avoid conflicts with other applications
3. **Local Testing**: Enables realistic integration tests on your local machine
4. **CI/CD Integration**: Simplifies automated testing in continuous integration pipelines
5. **Cloud Deployment**: Streamlines deployment to cloud environments

## Docker Basics
- **Image**: Read-only template containing application code, libraries, dependencies, and tools
- **Container**: Running instance of an image with its own filesystem, network, and isolated process space
- **Dockerfile**: Text file with instructions to build a Docker image
- **Registry**: Repository for storing and sharing Docker images (e.g., Docker Hub)

## Docker Compose

### Core Concepts
- **Docker Compose**: Tool for defining and running multi-container Docker applications
- **docker-compose.yml**: YAML configuration file that defines services, networks, and volumes
- **Services**: Individual containers defined in the compose file

### Key Commands
- `docker-compose up`: Create and start containers
- `docker-compose down`: Stop and remove containers
- `docker-compose build`: Build or rebuild services
- `docker-compose logs`: View output from containers
- `docker-compose ps`: List running containers

### YAML Structure

```yaml
services:     # Define containers
  service1:
    image: nginx
    ports:
      - "8080:80"
  service2:
    build: ./dir
    volumes:
      - ./data:/app/data
networks:     # Define custom networks
  my-network:
    driver: bridge
volumes:      # Define persistent volumes
  db-data:
```

### Important Elements
- **image**: Specify Docker image to use
- **build**: Build from Dockerfile
- **ports**: Map container ports to host
- **volumes**: Mount host directories into container
- **environment**: Set environment variables
- **depends_on**: Define service dependencies
- **networks**: Connect to specific networks
- **command**: Override default command

### Best Practices
- Use environment variables for configuration
- Create separate networks to isolate services
- Implement proper startup order with depends_on
- Use volumes for data persistence
- Use descriptive container names for easier reference and debugging

## Terraform
- Infrastructure as a code tool that lets you provision resources for both cloud and in-premise in human readable form.
- The code can then be shared, maintained, versioned and reused

### Why Terraform
- Simplifies infrastructure maintenance
- It's much easier to collaborate as it's simply a file and code
- Allows reproducibility
- Helps in clean-up, removes resources when not needed


Local Machine ➡ Terraform ➡ Service Provider (AWS, GCP,..)

### Terraform Core Concepts

#### Terraform Workflow

1. **`Write`** - Define resources in configuration files
2. **`Plan`** - Preview changes before applying
3. **`Apply`** - Create or update infrastructure
4. **`Destroy`** - Tear down resources when no longer needed

#### Key Components

- **Provider**: Plugin that interacts with APIs (Google Cloud in our case)
- **Resource**: Infrastructure object managed by Terraform (e.g., a VM, bucket, or database)
- **Data Source**: Read-only information fetched from providers
- **Module**: Reusable, encapsulated collection of resources
- **State**: Terraform's record of managed infrastructure

### Terraform with GCP

#### Basic Configuration

```terraform
# main.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  credentials = file("path/to/service-account-key.json")
  project     = "your-gcp-project-id"
  region      = "us-central1"
}
```

#### Essential Commands

```bash
terraform init      # Initialize working directory
terraform plan      # Preview changes
terraform apply     # Apply changes
terraform destroy   # Remove all resources
```

#### Cloud Storage (GCS)

```terraform
# Create a storage bucket for data lake
resource "google_storage_bucket" "data_lake" {
  name          = "company-data-lake" # should be universally unique
  location      = "US"
  storage_class = "STANDARD"
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
}

# Create a folder structure within the bucket
resource "google_storage_bucket_object" "raw_folder" {
  name    = "raw/"
  bucket  = google_storage_bucket.data_lake.name
  content = " "  # Empty content as we're just creating a prefix
}
```

#### BigQuery

```terraform
# Create a dataset
resource "google_bigquery_dataset" "analytics" {
  dataset_id                  = "analytics_data"
  friendly_name               = "Analytics Data"
  description                 = "Dataset for analytics workloads"
  location                    = "US"
  default_table_expiration_ms = 2592000000  # 30 days

  access {
    role          = "OWNER"
    user_by_email = "data-engineer@your-company.com"
  }
  
  access {
    role          = "READER"
    group_by_email = "analysts@your-company.com"
  }
}

# Create a table
resource "google_bigquery_table" "sales" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "sales_data"
  
  schema = <<EOF
[
  {
    "name": "transaction_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "amount",
    "type": "FLOAT",
    "mode": "REQUIRED"
  },
  {
    "name": "transaction_date",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  }
]
EOF
}
```

#### Dataproc (Managed Spark)

```terraform
# Create a Dataproc cluster
resource "google_dataproc_cluster" "spark_cluster" {
  name     = "spark-processing-cluster"
  region   = "us-central1"
  
  cluster_config {
    staging_bucket = google_storage_bucket.data_lake.name
    
    master_config {
      num_instances = 1
      machine_type  = "n1-standard-4"
      disk_config {
        boot_disk_size_gb = 100
      }
    }
    
    worker_config {
      num_instances = 2
      machine_type  = "n1-standard-4"
      disk_config {
        boot_disk_size_gb = 100
      }
    }
    
    software_config {
      image_version = "2.0-debian10"
      optional_components = ["JUPYTER"]
      
      override_properties = {
        "dataproc:dataproc.allow.zero.workers" = "true"
      }
    }
  }
}
```

#### Cloud Composer (Managed Airflow)

```terraform
# Create a Cloud Composer environment
resource "google_composer_environment" "airflow" {
  name   = "data-orchestration"
  region = "us-central1"
  
  config {
    node_config {
      zone         = "us-central1-a"
      machine_type = "n1-standard-2"
    }
    
    software_config {
      image_version = "composer-2.0.0-airflow-2.1.4"
      
      pypi_packages = {
        "pandas" = "==1.3.5"
        "gcsfs"  = "==2022.1.0"
      }
      
      env_variables = {
        "AIRFLOW__CORE__LOAD_EXAMPLES" = "False"
      }
    }
  }
}
```

#### Data Transfer Service

```terraform
# Set up a scheduled transfer from S3 to GCS
resource "google_storage_transfer_job" "s3_to_gcs_nightly" {
  description = "Nightly transfer from S3 to GCS"
  
  transfer_spec {
    aws_s3_data_source {
      bucket_name = "source-bucket"
      aws_access_key {
        access_key_id     = var.aws_access_key
        secret_access_key = var.aws_secret_key
      }
    }
    
    gcs_data_sink {
      bucket_name = google_storage_bucket.data_lake.name
      path        = "raw/s3-ingestion/"
    }
  }
  
  schedule {
    schedule_start_date {
      year  = 2023
      month = 1
      day   = 1
    }
    
    start_time_of_day {
      hours   = 1
      minutes = 0
      seconds = 0
      nanos   = 0
    }
    
    repeat_interval = "86400s"  # Daily
  }
}
```

