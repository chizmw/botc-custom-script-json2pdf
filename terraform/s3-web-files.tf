locals {
  files = {
    "index.html"             = "text/html"
    "script.js"              = "application/javascript"
    "styles.css"             = "text/css"
    "images/storyteller.png" = "image/png"
  }
}

resource "aws_s3_object" "botc_www_files" {
  depends_on = [
    aws_s3_bucket_policy.www_bucket_policy,
  ]
  for_each = local.files

  bucket       = aws_s3_bucket.www_bucket.id
  key          = each.key
  source       = "../www/${each.key}"
  content_type = each.value
  acl          = "public-read"
  etag         = filemd5("../www/${each.key}")
}
