resource "aws_iam_role" "iam_for_inference_lambda" {
  name = "yoloInferenceLambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "inference_lambda_policy" {
  name = "yoloAMRPolicy"
  description = "Allows access to logs and data source S3 bucket"
  policy = templatefile("./inference_lambda_policy.json", {
    sourcebucket= aws_s3_bucket.inference_source.id
  })
}

resource "aws_iam_role_policy_attachment" "attach_inference_lambda_policy" {
  role       = aws_iam_role.iam_for_inference_lambda.name
  policy_arn = aws_iam_policy.inference_lambda_policy.arn
}

resource "aws_lambda_function" "inference_lambda" {
  filename = "lambda.zip"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  function_name = "yoloAMR"
  role          = aws_iam_role.iam_for_inference_lambda.arn
  handler       = "yolo.handler"

  runtime = "python3.7"
  timeout=300
  memory_size=3008

}

data "archive_file" "lambda_zip" {
    type        = "zip"
    source_dir  = "src"
    output_path = "lambda.zip"
}


# API Gateway
resource "aws_api_gateway_rest_api" "api" {
  name = "yoloAMR"
}

resource "aws_api_gateway_resource" "resource" {
  path_part   = "resource"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

resource "aws_api_gateway_method" "method" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.resource.id
  http_method             = aws_api_gateway_method.method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.inference_lambda.invoke_arn
}

# Lambda
resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.inference_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${local.region}:${local.acccountId}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.method.http_method}${aws_api_gateway_resource.resource.path}"
}


resource "aws_s3_bucket" "inference_source" {
  bucket = local.inference_source_bucket_name
  acl    = "private"
  lifecycle {
    prevent_destroy = false
  }
  versioning {
    enabled = false
  }
}