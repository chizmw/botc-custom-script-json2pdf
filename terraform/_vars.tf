

variable "aws_region" {
  type        = string
  description = "The AWS region to deploy to."
  default     = "eu-west-2"
}
variable "domain_name" {
  type    = string
  default = "arcane-scripts.net"
}

variable "Xsite_name" {
  type    = string
  default = "make"
}

variable "www_domain_name" {
  type        = string
  description = "The domain name for the website."
  default     = "arcane-scripts.net"
}

variable "www_bucket_name" {
  type        = string
  description = "The name of the bucket without the www. prefix. Normally domain_name."
  default     = "arcane-scripts.net"
}


variable "common_tags" {
  description = "Common tags you want applied to all components."
  default = {
    "X-Foo"     = "botc-www"
    "X-Article" = "https://www.alexhyett.com/terraform-s3-static-website-hosting/"
  }
}


variable "sls_service_name" {
  type        = string
  description = "The name of the serverless service."
  default     = "botc-custom-script-json2pdf"
}

variable "sls_function_name" {
  type        = string
  description = "The name of the serverless function."
  default     = "botc-json2pdf"
}
