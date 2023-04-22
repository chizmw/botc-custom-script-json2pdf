terraform {
  backend "s3" {
    bucket = "436158765452-terraform-state"
    key    = "states/chizography-botcjson2pdf"
    region = "eu-west-2"
  }

  required_version = "~> 1.2"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "eu-west-2"
  default_tags {
    tags = local.default_tags
  }
}
