# create an IAM user group called BOTC_json2pdf which attaches an existing policy called AllowAssumeJson2PdfRole
resource "aws_iam_group" "group-botc_json2pdf" {
  name = "BOTC_json2pdf"
  path = "/botc/"
}
