output "bucket_name" {
  description = "S3 Bucket name"
  value       = aws_s3_bucket.files.bucket
}

output "file_system_id" {
  description = "S3 Files file system ID"
  value       = aws_s3files_file_system.main.id
}

output "access_point_arn" {
  description = "S3 Files access point ARN"
  value       = aws_s3files_access_point.lambda.arn
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.mount.function_name
}

output "lambda_function_url" {
  description = "Lambda Function URL (S3 Files)"
  value       = aws_lambda_function_url.mount.function_url
}

output "lambda_sdk_function_name" {
  description = "Lambda SDK function name"
  value       = aws_lambda_function.sdk.function_name
}

output "lambda_sdk_function_url" {
  description = "Lambda Function URL (SDK)"
  value       = aws_lambda_function_url.sdk.function_url
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "dashboard_url" {
  description = "CloudWatch Dashboard URL"
  value       = "https://${var.region}.console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.benchmark.dashboard_name}"
}
