# create an IAM policy called AllowAssumeJson2PdfRole
resource "aws_iam_policy" "policy-AllowAssumeJson2PdfRole" {
  name        = "AllowAssumeJson2PdfRole"
  path        = "/botc/"
  description = "Allow Chizography Admin to assume the Json2Pdf role"
  policy      = data.aws_iam_policy_document.policydoc-AllowAssumeJson2PdfRole.json
}

resource "aws_iam_policy" "policy-Deploy_FineGrainedExtras_policy" {
  name   = "AllowBOTCDeployExtras"
  path   = "/botc/"
  policy = data.aws_iam_policy_document.policydoc-deploy_json2pdf_finegrained_extras.json
}
