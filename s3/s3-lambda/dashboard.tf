# ===========================
# CloudWatch Dashboard
# ===========================
resource "aws_cloudwatch_dashboard" "benchmark" {
  dashboard_name = "${local.name}-benchmark"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 1
        properties = {
          markdown = "# S3 Files vs SDK (boto3) - Lambda Benchmark"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 1
        width  = 24
        height = 6
        properties = {
          title   = "Duration Comparison (ms)"
          region  = var.region
          view    = "table"
          stacked = false
          period  = 300
          stat    = "Average"
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.mount.function_name, { label = "S3 Files - Avg" }],
            ["...", { stat = "p50", label = "S3 Files - P50" }],
            ["...", { stat = "p95", label = "S3 Files - P95" }],
            ["...", { stat = "Maximum", label = "S3 Files - Max" }],
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.sdk.function_name, { label = "SDK - Avg" }],
            ["...", { stat = "p50", label = "SDK - P50" }],
            ["...", { stat = "p95", label = "SDK - P95" }],
            ["...", { stat = "Maximum", label = "SDK - Max" }]
          ]
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 7
        width  = 24
        height = 6
        properties = {
          title  = "Invocations & Errors"
          region = var.region
          view   = "table"
          period = 300
          stat   = "Sum"
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.mount.function_name, { label = "S3 Files - Invocations" }],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.mount.function_name, { label = "S3 Files - Errors" }],
            ["AWS/Lambda", "Throttles", "FunctionName", aws_lambda_function.mount.function_name, { label = "S3 Files - Throttles" }],
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.sdk.function_name, { label = "SDK - Invocations" }],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.sdk.function_name, { label = "SDK - Errors" }],
            ["AWS/Lambda", "Throttles", "FunctionName", aws_lambda_function.sdk.function_name, { label = "SDK - Throttles" }]
          ]
        }
      }
    ]
  })
}
