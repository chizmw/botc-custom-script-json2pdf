# resource "aws_s3_bucket" "www_bucket" {
#   bucket = "${var.site_name}.${var.www_bucket_name}"
# }

# resource "aws_s3_bucket_ownership_controls" "www_bucket_ownership_controls" {
#   bucket = aws_s3_bucket.www_bucket.id

#   rule {
#     object_ownership = "BucketOwnerPreferred"
#   }
# }

# resource "aws_s3_bucket_acl" "www_bucket_acl" {
#   depends_on = [
#     aws_s3_bucket_ownership_controls.www_bucket_ownership_controls,
#   ]
#   bucket = aws_s3_bucket.www_bucket.id
#   acl    = "public-read"
# }

# resource "aws_s3_bucket_policy" "www_bucket_policy" {
#   depends_on = [
#     aws_s3_bucket_acl.www_bucket_acl,
#   ]
#   bucket = aws_s3_bucket.www_bucket.id
#   policy = templatefile("templates/s3-policy.json", { bucket = "${var.site_name}.${var.www_bucket_name}" })
# }

# resource "aws_s3_bucket_cors_configuration" "www_bucket_cors" {
#   bucket = aws_s3_bucket.www_bucket.id

#   cors_rule {
#     allowed_headers = ["Authorization", "Content-Length"]
#     allowed_methods = ["GET", "POST"]
#     allowed_origins = ["https://${var.site_name}.${var.www_domain_name}"]
#     max_age_seconds = 3000
#   }
# }

# resource "aws_s3_bucket_website_configuration" "www_bucket_website" {
#   bucket = aws_s3_bucket.www_bucket.id

#   index_document {
#     suffix = "index.html"
#   }
#   error_document {
#     key = "404.html"
#   }
# }


# # S3 bucket for redirecting non-www to www.
# resource "aws_s3_bucket" "root_bucket" {
#   bucket = var.www_domain_name
#   #acl    = "public-read"
#   #policy = templatefile("templates/s3-policy.json", { bucket = var.www_bucket_name })

#   /*website {
#     redirect_all_requests_to = "https://www.${var.www_domain_name}"
#   }*/
# }
# resource "aws_s3_bucket_website_configuration" "root_bucket_website" {
#   bucket = aws_s3_bucket.root_bucket.id
#   redirect_all_requests_to {
#     host_name = "https://${var.site_name}.${var.www_domain_name}"
#     protocol  = "https"
#   }
# }

# resource "aws_s3_bucket_ownership_controls" "root_bucket_ownership_controls" {
#   bucket = aws_s3_bucket.root_bucket.id

#   rule {
#     object_ownership = "BucketOwnerPreferred"
#   }
# }

# resource "aws_s3_bucket_acl" "root_bucket_acl" {
#   depends_on = [
#     aws_s3_bucket_ownership_controls.root_bucket_ownership_controls
#   ]
#   bucket = aws_s3_bucket.root_bucket.id
#   acl    = "public-read"
# }

# resource "aws_s3_bucket_policy" "root_bucket_policy" {
#   depends_on = [
#     aws_s3_bucket_acl.root_bucket_acl
#   ]
#   bucket = aws_s3_bucket.root_bucket.id
#   policy = templatefile("templates/s3-policy.json", { bucket = var.www_bucket_name })
# }


# # Uncomment the validation_record_fqdns line if you do DNS validation instead of Email.

# # Cloudfront distribution for main s3 site.
# resource "aws_cloudfront_distribution" "www_s3_distribution" {
#   origin {
#     domain_name = aws_s3_bucket.www_bucket.bucket_regional_domain_name
#     origin_id   = "S3-${var.site_name}.${var.www_bucket_name}"

#     custom_origin_config {
#       http_port              = 80
#       https_port             = 443
#       origin_protocol_policy = "http-only"
#       origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
#     }
#   }

#   enabled             = true
#   is_ipv6_enabled     = true
#   default_root_object = "index.html"

#   aliases = ["${var.site_name}.${var.www_domain_name}"]

#   custom_error_response {
#     error_caching_min_ttl = 0
#     error_code            = 404
#     response_code         = 200
#     response_page_path    = "/404.html"
#   }

#   default_cache_behavior {
#     allowed_methods  = ["GET", "HEAD"]
#     cached_methods   = ["GET", "HEAD"]
#     target_origin_id = "S3-${var.site_name}.${var.www_bucket_name}"

#     forwarded_values {
#       query_string = false

#       cookies {
#         forward = "none"
#       }
#     }

#     viewer_protocol_policy = "redirect-to-https"
#     min_ttl                = 31536000
#     default_ttl            = 31536000
#     max_ttl                = 31536000
#     compress               = true
#   }

#   restrictions {
#     geo_restriction {
#       restriction_type = "none"
#     }
#   }

#   viewer_certificate {
#     #acm_certificate_arn      = aws_acm_certificate_validation.cert_validation.certificate_arn
#     acm_certificate_arn      = data.aws_acm_certificate.star_domain.arn
#     ssl_support_method       = "sni-only"
#     minimum_protocol_version = "TLSv1.1_2016"
#   }
# }

# # Cloudfront S3 for redirect to www.
# resource "aws_cloudfront_distribution" "root_s3_distribution" {
#   origin {
#     domain_name = aws_s3_bucket.root_bucket.bucket_regional_domain_name
#     origin_id   = "S3-.${var.www_bucket_name}"
#     custom_origin_config {
#       http_port              = 80
#       https_port             = 443
#       origin_protocol_policy = "http-only"
#       origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
#     }
#   }

#   enabled         = true
#   is_ipv6_enabled = true

#   aliases = [var.www_domain_name]

#   default_cache_behavior {
#     allowed_methods  = ["GET", "HEAD"]
#     cached_methods   = ["GET", "HEAD"]
#     target_origin_id = "S3-.${var.www_bucket_name}"

#     forwarded_values {
#       query_string = true

#       cookies {
#         forward = "none"
#       }

#       headers = ["Origin"]
#     }

#     viewer_protocol_policy = "allow-all"
#     min_ttl                = 0
#     default_ttl            = 86400
#     max_ttl                = 31536000
#   }

#   restrictions {
#     geo_restriction {
#       restriction_type = "none"
#     }
#   }

#   viewer_certificate {
#     acm_certificate_arn      = data.aws_acm_certificate.star_domain.arn
#     ssl_support_method       = "sni-only"
#     minimum_protocol_version = "TLSv1.1_2016"
#   }
# }
