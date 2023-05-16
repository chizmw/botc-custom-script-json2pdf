locals {
  files = {
    "index.html"             = "text/html"
    "script.js"              = "application/javascript"
    "custom.js"              = "application/javascript"
    "styles.css"             = "text/css"
    "images/storyteller.png" = "image/png"
    "images/download.png"    = "image/png"
    "images/background.png"  = "image/png"
    "images/infobutton.png"  = "image/png"
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

  tags = {
    "BelongsToDist" = aws_cloudfront_distribution.wkspc_www_s3_distribution.id
  }
}

# we need to create an s3 file/object (const.js) that contains the API Gateway
# URL so that the web page can call the API Gateway
resource "aws_s3_object" "botc_www_const_js" {
  depends_on = [
    aws_s3_bucket_policy.wkspc_www_bucket_policy,
    aws_api_gateway_stage.api_stage,
  ]
  bucket       = aws_s3_bucket.wkspc_www_bucket.id
  key          = "const.js"
  content      = <<EOF
/* generated by terraform */
const API_GATEWAY_URL = "${aws_api_gateway_stage.api_stage.invoke_url}";
EOF
  content_type = "application/javascript"
  acl          = "public-read"
}
