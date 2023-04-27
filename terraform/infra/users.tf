# create an IAM user called botc.json2pdf
resource "aws_iam_user" "user-botc_json2pdf" {
  name = "botc.json2pdf"
  path = "/botc/"
}

# add botc.json2pdf to the BOTC_json2pdf group
resource "aws_iam_user_group_membership" "BOTC_json2pdf" {
  user   = aws_iam_user.user-botc_json2pdf.name
  groups = [aws_iam_group.group-botc_json2pdf.name]
}
