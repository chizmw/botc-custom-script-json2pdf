# attach the AllowAssumeJson2PdfRole policy to the BOTC_json2pdf group
resource "aws_iam_group_policy_attachment" "AllowAssumeJson2PdfRole" {
  group      = aws_iam_group.group-botc_json2pdf.name
  policy_arn = aws_iam_policy.policy-AllowAssumeJson2PdfRole.arn
}

/* no longer attaching this policy to the BOTC_json2pdf group
   we'll attach it to the deploy_json2pdf role instead
resource "aws_iam_group_policy_attachment" "Deploy_FineGrainedExtras" {
  group      = aws_iam_group.group-botc_json2pdf.name
  policy_arn = aws_iam_policy.policy-Deploy_FineGrainedExtras_policy.arn
}
*/

# attach Deploy_FineGrainedExtras_policy to the deploy_json2pdf role
resource "aws_iam_role_policy_attachment" "Deploy_FineGrainedExtras" {
  role       = aws_iam_role.role-deploy_json2pdf.name
  policy_arn = aws_iam_policy.policy-Deploy_FineGrainedExtras_policy.arn
}
