# use SNS to send notification to the invalidate-cache lambda function when objects are created or modified in the S3 bucket
# data "aws_iam_policy_document" "topic_invalidate" {
#   statement {
#     effect = "Allow"

#     principals {
#       type        = "Service"
#       identifiers = ["s3.amazonaws.com"]
#     }

#     actions   = ["SNS:Publish"]
#     resources = ["arn:aws:sns:*:*:s3-event-notification-topic"]

#     condition {
#       test     = "ArnLike"
#       variable = "aws:SourceArn"
#       values   = [aws_s3_bucket.wkspc_www_bucket.arn]
#     }
#   }
# }

# resource "aws_sns_topic" "sns_invalidate_cache" {
#   name   = "invalidate-cache"
#   policy = data.aws_iam_policy_document.topic_invalidate.json
# }

# resource "aws_sns_topic_subscription" "sns_invalidate_cache_lambda" {
#   topic_arn = aws_sns_topic.sns_invalidate_cache.arn
#   protocol  = "lambda"
#   endpoint  = data.aws_lambda_function.lambda_invalidate_cache.arn
# }

# resource "aws_s3_bucket_notification" "bucket_notification" {
#   bucket = aws_s3_bucket.wkspc_www_bucket.id

#   lambda_function {
#     lambda_function_arn = data.aws_lambda_function.lambda_invalidate_cache.arn
#     events              = ["s3:ObjectCreated:*"]
#   }
# }


data "aws_lambda_function" "lambda_invalidate_cache" {
  function_name = "invalidate-cache"
}

data "aws_iam_role" "iam_for_lambda" {
  name = "deploy_json2pdf"
}

# data "aws_sns_topic" "sns_invalidate_cache" {
# name =
# }
