
variable "domain_name" {
  type    = string
  default = "arcane-scripts.net"
}

variable "site_name" {
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
