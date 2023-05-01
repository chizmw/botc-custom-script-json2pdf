data "aws_route53_zone" "main" {
  name = var.www_domain_name
}

resource "aws_route53_record" "root-a" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = var.www_domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.root_s3_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.root_s3_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "www-a" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${var.site_name}.${var.www_domain_name}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.www_s3_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.www_s3_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}


resource "aws_route53_record" "wkspc_www-a" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "${local.site_name}.${var.www_domain_name}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.wkspc_www_s3_distribution.domain_name
    zone_id                = aws_cloudfront_distribution.wkspc_www_s3_distribution.hosted_zone_id
    evaluate_target_health = false
  }
}
