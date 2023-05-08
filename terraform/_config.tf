terraform {
  backend "s3" {
    # don't set any values here (other than region)
    # we need to be using the same TF_CLI_ARGS_init as the workflows
    region = "eu-west-2"
    #bucket               = "436158765452-terraform-state"
    #key                  = "chizography-botcjson2pdf"
    #workspace_key_prefix = "tf-state"
  }

  required_version = "~> 1.4"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  alias  = "default"
  region = "eu-west-2"
  default_tags {
    tags = local.tag_defaults
  }
}

provider "aws" {
  alias  = "acm_provider"
  region = "us-east-1"
  default_tags {
    tags = local.tag_defaults
  }
}
