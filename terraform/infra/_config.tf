terraform {
  backend "s3" {
    bucket = "436158765452-terraform-state"
    key    = "states/chizography-botc-infra"
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
}

provider "aws" {
  alias  = "acm_provider"
  region = "us-east-1"
}
