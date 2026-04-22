terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" { state = "available" }

locals {
  name = "s3-lambda-files"
}

# ===========================
# VPC
# ===========================
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = "${local.name}-vpc" }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index + 1)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = { Name = "${local.name}-private-${count.index}" }
}

resource "aws_security_group" "lambda" {
  name_prefix = "${local.name}-lambda-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for Lambda with S3 Files access"

  ingress {
    description = "NFS from Lambda"
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    self        = true
  }

  egress {
    description = "NFS for S3 Files"
    from_port   = 2049
    to_port     = 2049
    protocol    = "tcp"
    self        = true
  }

  egress {
    description = "HTTPS for AWS services"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${local.name}-lambda-sg" }
}

# ===========================
# S3 Bucket
# ===========================
resource "aws_s3_bucket" "files" {
  bucket = "${local.name}-${data.aws_caller_identity.current.account_id}"

  tags = { Name = "${local.name}-bucket" }
}

resource "aws_s3_bucket_versioning" "files" {
  bucket = aws_s3_bucket.files.id

  versioning_configuration {
    status = "Enabled"
  }
}

# ===========================
# S3 Files - IAM Role
# ===========================
resource "aws_iam_role" "s3files" {
  name = "${local.name}-s3files-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "elasticfilesystem.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "s3files" {
  name = "${local.name}-s3files-policy"
  role = aws_iam_role.s3files.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "s3:*"
      Resource = [aws_s3_bucket.files.arn, "${aws_s3_bucket.files.arn}/*"]
    }]
  })
}

# ===========================
# S3 Files - File System
# ===========================
resource "aws_s3files_file_system" "main" {
  bucket   = aws_s3_bucket.files.arn
  role_arn = aws_iam_role.s3files.arn

  tags = { Name = "${local.name}-fs" }

  depends_on = [aws_s3_bucket_versioning.files]
}

# ===========================
# S3 Files - Mount Targets
# ===========================
resource "aws_s3files_mount_target" "main" {
  count = 2

  file_system_id  = aws_s3files_file_system.main.id
  subnet_id       = aws_subnet.private[count.index].id
  security_groups = [aws_security_group.lambda.id]
}

# ===========================
# S3 Files - Access Point
# ===========================
resource "aws_s3files_access_point" "lambda" {
  file_system_id = aws_s3files_file_system.main.id

  posix_user {
    uid = 1000
    gid = 1000
  }

  root_directory {
    path = "/lambda"

    creation_permissions {
      owner_uid   = 1000
      owner_gid   = 1000
      permissions = "755"
    }
  }

  tags = { Name = "${local.name}-ap" }
}

# ===========================
# Lambda - IAM Role
# ===========================
resource "aws_iam_role" "lambda" {
  name = "${local.name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "lambda" {
  name = "${local.name}-lambda-policy"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3files:ClientMount", "s3files:ClientWrite"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectVersion", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
        Resource = [aws_s3_bucket.files.arn, "${aws_s3_bucket.files.arn}/*"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_vpc" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ===========================
# Lambda Function
# ===========================
data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "mount" {
  function_name    = "${local.name}-mount"
  role             = aws_iam_role.lambda.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.9"
  timeout          = 30
  memory_size      = 512
  filename         = data.archive_file.lambda.output_path
  source_code_hash = data.archive_file.lambda.output_base64sha256

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  file_system_config {
    arn              = aws_s3files_access_point.lambda.arn
    local_mount_path = "/mnt/s3files"
  }

  environment {
    variables = {
      MOUNT_PATH  = "/mnt/s3files"
      BUCKET_NAME = aws_s3_bucket.files.bucket
    }
  }

  depends_on = [aws_s3files_mount_target.main]
}

# ===========================
# Lambda Function URL (S3 Files)
# ===========================
resource "aws_lambda_function_url" "mount" {
  function_name      = aws_lambda_function.mount.function_name
  authorization_type = "NONE"
}

# ===========================
# Lambda Function (SDK)
# ===========================
data "archive_file" "lambda_sdk" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_sdk"
  output_path = "${path.module}/lambda_sdk.zip"
}

resource "aws_lambda_function" "sdk" {
  function_name    = "${local.name}-sdk"
  role             = aws_iam_role.lambda.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.9"
  timeout          = 30
  memory_size      = 512
  filename         = data.archive_file.lambda_sdk.output_path
  source_code_hash = data.archive_file.lambda_sdk.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.files.bucket
    }
  }
}

# ===========================
# Lambda Function URL (SDK)
# ===========================
resource "aws_lambda_function_url" "sdk" {
  function_name      = aws_lambda_function.sdk.function_name
  authorization_type = "NONE"
}
