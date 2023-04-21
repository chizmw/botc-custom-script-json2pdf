# create an IAM role called deploy_json2pdf
resource "aws_iam_role" "deploy_json2pdf" {
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
  assume_role_policy = data.aws_iam_policy_document.trust_relationships_deploy_json2pdf.json
}
data "aws_iam_policy_document" "trust_relationships_deploy_json2pdf" {
  statement {
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::436158765452:root"]
    }
    actions = ["sts:AssumeRole"]
  }

  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}



# create an IAM user group called BOTC_json2pdf which attaches an existing policy called AllowAssumeJson2PdfRole
resource "aws_iam_group" "BOTC_json2pdf" {
  name = "BOTC_json2pdf"
  path = "/botc/"
}


# create an IAM policy called AllowAssumeJson2PdfRole
resource "aws_iam_policy" "AllowAssumeJson2PdfRole" {
  name        = "AllowAssumeJson2PdfRole"
  path        = "/botc/"
  description = "Allow Chizography Admin to assume the Json2Pdf role"
  policy      = data.aws_iam_policy_document.AllowAssumeJson2PdfRole.json
}

data "aws_iam_policy_document" "AllowAssumeJson2PdfRole" {
  statement {
    sid    = "AllowAssumeJson2PdfRole"
    effect = "Allow"
    actions = [
      "sts:AssumeRole",
      "sts:TagSession",
      "sts:GetSessionToken"
    ]
    resources = [aws_iam_role.deploy_json2pdf.arn]
  }
}

# attach the AllowAssumeJson2PdfRole policy to the BOTC_json2pdf group
resource "aws_iam_group_policy_attachment" "AllowAssumeJson2PdfRole" {
  group      = aws_iam_group.BOTC_json2pdf.name
  policy_arn = aws_iam_policy.AllowAssumeJson2PdfRole.arn
}

# create an IAM user called botc.json2pdf
resource "aws_iam_user" "botc_json2pdf" {
  name = "botc.json2pdf"
  path = "/botc/"

  tags = {
    "AKIAxxxxxxxxAZFBWEWB" = "botc-json2pdf-deploy"
  }
}

# add botc.json2pdf to the BOTC_json2pdf group
resource "aws_iam_user_group_membership" "BOTC_json2pdf" {
  user   = aws_iam_user.botc_json2pdf.name
  groups = [aws_iam_group.BOTC_json2pdf.name]
}
