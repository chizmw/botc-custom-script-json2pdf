data "aws_route53_zone" "main" {
  name = var.www_domain_name
}
