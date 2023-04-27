# the policy data to use for the assume role policy
data "aws_iam_policy_document" "policydoc-trust_relationships_deploy_json2pdf" {
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

# create a policy called deploy_json2pdf_finegrained_extras
data "aws_iam_policy_document" "policydoc-deploy_json2pdf_finegrained_extras" {
  statement {
    effect = "Allow"
    actions = [
      "acm:AddTagsToCertificate",
      "acm:DescribeCertificate",
      "acm:ListTagsForCertificate",
      "acm:RequestCertificate",
      "cloudfront:GetDistribution",
      "cloudfront:ListTagsForResource",
      "iam:CreatePolicy",
      "iam:CreatePolicyVersion",
      "iam:DeletePolicyVersion",
      "iam:DetachRolePolicy",
      "iam:GetGroup",
      "iam:GetUser",
      "iam:ListAttachedGroupPolicies",
      "iam:ListGroupsForUser",
      "iam:TagPolicy",
      "route53:ChangeResourceRecordSets",
      "route53:GetChange",
      "route53:GetHostedZone",
      "route53:ListHostedZones",
      "route53:ListResourceRecordSets",
      "route53:ListTagsForResource",
      "s3:PutBucketAcl",
      "s3:PutBucketPolicy",
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "policydoc-trust_relationships_apig_json2pdf" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "policydoc-trust_relationships_lambda_json2pdf" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "policydoc-AllowAssumeJson2PdfRole" {
  statement {
    sid    = "AllowAssumeJson2PdfRole"
    effect = "Allow"
    actions = [
      "sts:AssumeRole",
      "sts:TagSession",
      "sts:GetSessionToken"
    ]
    resources = [aws_iam_role.role-deploy_json2pdf.arn]
  }
}
