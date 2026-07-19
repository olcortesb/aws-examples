terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = ">= 2.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  default = "us-east-1"
}

locals {
  name = "lambda-self-managed-storage"
}

data "aws_caller_identity" "current" {}

# ===========================
# S3 Bucket
# ===========================
resource "aws_s3_bucket" "code" {
  bucket        = "${local.name}-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
}

resource "aws_s3_bucket_versioning" "code" {
  bucket = aws_s3_bucket.code.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_lifecycle_configuration" "code" {
  bucket     = aws_s3_bucket.code.id
  depends_on = [aws_s3_bucket_versioning.code]

  rule {
    id     = "cleanup-old-versions"
    status = "Enabled"
    filter { prefix = "deployments/" }
    noncurrent_version_expiration {
      noncurrent_days           = 14
      newer_noncurrent_versions = 2
    }
  }
}

resource "aws_s3_bucket_policy" "code" {
  bucket     = aws_s3_bucket.code.id
  depends_on = [aws_s3_bucket_versioning.code]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "LambdaSelfManagedCodeAccess"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = ["s3:GetObject", "s3:GetObjectVersion"]
      Resource  = "${aws_s3_bucket.code.arn}/deployments/*"
      Condition = {
        StringEquals = {
          "aws:SourceAccount" = data.aws_caller_identity.current.account_id
        }
      }
    }]
  })
}

# ===========================
# Lambda zip → S3
# ===========================
data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_s3_object" "lambda_code" {
  bucket     = aws_s3_bucket.code.id
  key        = "deployments/app.zip"
  source     = data.archive_file.lambda.output_path
  etag       = data.archive_file.lambda.output_md5
  depends_on = [aws_s3_bucket_versioning.code]
}

# ===========================
# Outputs
# ===========================
output "bucket_name" {
  value = aws_s3_bucket.code.id
}

output "s3_key" {
  value = aws_s3_object.lambda_code.key
}

output "s3_object_version" {
  value = aws_s3_object.lambda_code.version_id
}
