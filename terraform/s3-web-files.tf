locals {
  files = {
    "index.html"             = "text/html"
    "script.js"              = "application/javascript"
    "styles.css"             = "text/css"
    "images/storyteller.png" = "image/png"
    "images/download.png"    = "image/png"
    "images/background.png"  = "image/png"
    "dropzone.css"           = "text/css"

    # favicon resources
    "favicon/android-chrome-192x192.png" = "image/png"
    "favicon/android-chrome-512x512.png" = "image/png"
    "favicon/apple-touch-icon.png"       = "image/png"
    "favicon/favicon-16x16.png"          = "image/png"
    "favicon/favicon-32x32.png"          = "image/png"
    "favicon/favicon.ico"                = "image/x-icon"
    "favicon/site.webmanifest"           = "application/manifest+json"

  }
}

# resource "aws_s3_object" "botc_www_files" {
#   depends_on = [
#     aws_s3_bucket_policy.www_bucket_policy,
#   ]
#   for_each = local.files

#   bucket       = aws_s3_bucket.www_bucket.id
#   key          = each.key
#   source       = "../www/${each.key}"
#   content_type = each.value
#   acl          = "public-read"
#   etag         = filemd5("../www/${each.key}")
#}

resource "aws_s3_object" "wkspc_botc_www_files" {
  depends_on = [
    aws_s3_bucket_policy.wkspc_www_bucket_policy,
  ]
  for_each = local.files

  bucket       = aws_s3_bucket.wkspc_www_bucket.id
  key          = each.key
  source       = "../www/${each.key}"
  content_type = each.value
  acl          = "public-read"
  etag         = filemd5("../www/${each.key}")
}
