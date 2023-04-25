
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
    allowed_origins = ["https://${local.host_name}", "http://json2pdf.tower.theboardingparty.com.s3-website.eu-west-2.amazonaws.com/"]
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
    "index.html"             = "text/html"
    "script.js"              = "application/javascript"
    "styles.css"             = "text/css"
    "images/storyteller.png" = "image/png"
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

# SSL Certificate
resource "aws_acm_certificate" "ssl_certificate" {
  provider                  = aws.acm_provider
  domain_name               = var.domain_name
  subject_alternative_names = ["*.${var.domain_name}"]
  validation_method         = "EMAIL"
  #validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# Uncomment the validation_record_fqdns line if you do DNS validation instead of Email.
resource "aws_acm_certificate_validation" "cert_validation" {
  provider        = aws.acm_provider
  certificate_arn = aws_acm_certificate.ssl_certificate.arn
  #validation_record_fqdns = [for record in aws_route53_record.cert_validation : record.fqdn]
}


# Cloudfront distribution for main s3 site.
resource "aws_cloudfront_distribution" "www_s3_distribution" {
  origin {
    domain_name = aws_s3_bucket_website_configuration.botc_www_config.website_endpoint
    origin_id   = "S3-www.${var.domain_name}"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  aliases = ["${var.site_name}.${var.domain_name}"]

  custom_error_response {
    error_caching_min_ttl = 0
    error_code            = 404
    response_code         = 200
    response_page_path    = "/404.html"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-www.${var.domain_name}"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 31536000
    default_ttl            = 31536000
    max_ttl                = 31536000
    compress               = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.cert_validation.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.1_2016"
  }
}

# Cloudfront S3 for redirect to www.
resource "aws_cloudfront_distribution" "root_s3_distribution" {
  origin {
    domain_name = aws_s3_bucket_website_configuration.botc_www_config.website_endpoint
    origin_id   = "S3-.${var.domain_name}"
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }
  }

  enabled         = true
  is_ipv6_enabled = true

  aliases = [var.domain_name]

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-.${var.domain_name}"

    forwarded_values {
      query_string = true

      cookies {
        forward = "none"
      }

      headers = ["Origin"]
    }

    viewer_protocol_policy = "allow-all"
    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.cert_validation.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.1_2016"
  }

}
