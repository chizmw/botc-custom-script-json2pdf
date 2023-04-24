variable "domain_name" {
  type    = string
  default = "tower.theboardingparty.com"
}

variable "site_name" {
  type    = string
  default = "json2pdf"
}

locals {
  host_name = "${var.site_name}.${var.domain_name}"
}

# data lookup for route 53 hosted zone
data "aws_route53_zone" "tower" {
  name         = var.domain_name
  private_zone = false
}

# create a dns alias for the bucket
resource "aws_route53_record" "botc_www_alias_record" {
  zone_id = data.aws_route53_zone.tower.zone_id
  name    = aws_s3_bucket.botc_www_bucket.bucket
  type    = "A"
  alias {
    name                   = aws_s3_bucket_website_configuration.botc_www_config.website_endpoint
    zone_id                = aws_s3_bucket.botc_www_bucket.hosted_zone_id
    evaluate_target_health = true
  }
}


# create an s3 bucket for the generated PDF files
resource "aws_s3_bucket" "botc_www_bucket" {
  bucket   = local.host_name
  provider = aws
}

resource "aws_s3_bucket_public_access_block" "botc_www_bucket_public_access_block" {
  bucket = aws_s3_bucket.botc_www_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_website_configuration" "botc_www_config" {
  depends_on = [
    aws_s3_bucket_public_access_block.botc_www_bucket_public_access_block
  ]
  bucket = aws_s3_bucket.botc_www_bucket.id
  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_cors_configuration" "example" {
  bucket = aws_s3_bucket.botc_www_bucket.id
  cors_rule {
    allowed_headers = ["Authorization", "Content-Length"]
    allowed_methods = ["GET", "POST"]
    allowed_origins = ["https://${local.host_name}"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_policy" "botc_www_policy" {
  bucket = aws_s3_bucket.botc_www_bucket.bucket
  policy = templatefile("s3-www-policy.json", { bucket = aws_s3_bucket.botc_www_bucket.bucket })
}

resource "aws_s3_bucket_ownership_controls" "botc_www_bucket_ownership_controls" {
  bucket = aws_s3_bucket.botc_www_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}


resource "aws_s3_bucket_acl" "botc_www_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.botc_www_bucket_ownership_controls
  ]
  bucket = aws_s3_bucket.botc_www_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_versioning" "botc_www_bucket_versioning" {
  bucket = aws_s3_bucket.botc_www_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}


locals {
  files = {
    "index.html"                 = "text/html"
    "script.js"                  = "application/javascript"
    "styles.css"                 = "text/css"
    "www/images/storyteller.png" = "image/png"
  }
}

resource "aws_s3_object" "botc_www_files" {
  depends_on = [
    aws_s3_bucket_public_access_block.botc_www_bucket_public_access_block
  ]
  for_each = local.files

  bucket       = aws_s3_bucket.botc_www_bucket.id
  key          = each.key
  source       = "../www/${each.key}"
  content_type = each.value
  acl          = "public-read"
  etag         = filemd5("../www/${each.key}")
}
