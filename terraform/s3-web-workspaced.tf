# a bucket for the $workspace files to be stored in

resource "aws_s3_bucket" "wkspc_www_bucket" {
  bucket = "${local.site_name}.${var.www_bucket_name}"
}

resource "aws_s3_bucket_ownership_controls" "wkspc_www_bucket_ownership_controls" {
  bucket = aws_s3_bucket.wkspc_www_bucket.id

  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "wkspc_www_bucket_acl" {
  depends_on = [
    aws_s3_bucket_ownership_controls.wkspc_www_bucket_ownership_controls,
  ]
  bucket = aws_s3_bucket.wkspc_www_bucket.id
  acl    = "public-read"
}

resource "aws_s3_bucket_policy" "wkspc_www_bucket_policy" {
  depends_on = [
    aws_s3_bucket_acl.wkspc_www_bucket_acl,
  ]
  bucket = aws_s3_bucket.wkspc_www_bucket.id
  policy = templatefile("templates/s3-policy.json", { bucket = "${local.site_name}.${var.www_bucket_name}" })
}

resource "aws_s3_bucket_cors_configuration" "wkspc_www_bucket_cors" {
  bucket = aws_s3_bucket.wkspc_www_bucket.id

  cors_rule {
    allowed_headers = ["Authorization", "Content-Length"]
    allowed_methods = ["GET", "POST"]
    allowed_origins = ["https://${local.site_name}.${var.www_domain_name}"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_website_configuration" "wkspc_www_bucket_website" {
  bucket = aws_s3_bucket.wkspc_www_bucket.id

  index_document {
    suffix = "index.html"
  }
  error_document {
    key = "404.html"
  }
}



resource "aws_cloudfront_distribution" "wkspc_www_s3_distribution" {
  origin {
    domain_name = aws_s3_bucket.wkspc_www_bucket.bucket_regional_domain_name
    origin_id   = "S3-${local.site_name}.${var.www_bucket_name}"

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

  aliases = ["${local.site_name}.${var.www_domain_name}"]

  custom_error_response {
    error_caching_min_ttl = 0
    error_code            = 404
    response_code         = 200
    response_page_path    = "/404.html"
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${local.site_name}.${var.www_bucket_name}"

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
    #acm_certificate_arn      = aws_acm_certificate_validation.cert_validation.certificate_arn
    acm_certificate_arn      = data.aws_acm_certificate.star_domain.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.1_2016"
  }
}

# we don't want to have to manually invalidate the cache every time we update the site
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.wkspc_www_bucket.id

  lambda_function {
    lambda_function_arn = "arn:aws:lambda:eu-west-2:436158765452:function:invalidate-cache"
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = ""
    filter_suffix       = ""
  }
}

# Add permission for S3 bucket to trigger Lambda function
resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowS3BucketToTriggerLambda-${local.site_name}-${terraform.workspace}"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.invalidate_cache.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.wkspc_www_bucket.arn
}
