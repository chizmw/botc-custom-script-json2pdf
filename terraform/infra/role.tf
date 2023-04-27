
# create an IAM role called deploy_json2pdf
resource "aws_iam_role" "role-deploy_json2pdf" {
  name        = "deploy_json2pdf"
  description = "Allows Lambda functions to call AWS services on your behalf."
  path        = "/botc/"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AWSCloudFormationFullAccess",
    "arn:aws:iam::aws:policy/AWSLambdaExecute",
    "arn:aws:iam::aws:policy/AWSLambda_FullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
  ]
  assume_role_policy = data.aws_iam_policy_document.policydoc-trust_relationships_deploy_json2pdf.json
}

resource "aws_iam_role" "role-apig_json2pdf" {
  name        = "apig_json2pdf"
  description = "Allows API Gateway to call AWS services on your behalf."
  path        = "/botc/"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess",
  ]
  assume_role_policy = data.aws_iam_policy_document.policydoc-trust_relationships_apig_json2pdf.json
}


resource "aws_iam_role" "roleXXXXXX-lambda_json2pdf" {
  name        = "lambda_json2pdf"
  description = "Allows Lambda to call AWS services on your behalf."
  path        = "/botc/"
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess",
    "arn:aws:iam::aws:policy/AWSLambdaExecute",
  ]
  assume_role_policy = data.aws_iam_policy_document.policydoc-trust_relationships_lambda_json2pdf.json
}
