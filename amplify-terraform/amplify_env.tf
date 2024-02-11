# we want to update the ENV values we have set in our Amplify website
# that site is deployed separately, so we need to grab it via data{}
# and then update the ENV values

#data "aws_amplify_app" "app" {
#name = "site-arcane-scripts.net"
#}

# we set TEST_API_URL in the Amplify website to the API Gateway URL
# we use the invoke URL from the deployment resource to get the URL

resource "aws_amplify_branch" "main" {
  app_id      = aws_amplify_app.site-arcane-scripts-net.id
  branch_name = "main"
  stage       = "PRODUCTION"

  environment_variables = {
    JEKYLL_API_GATEWAY_URL = "https://9t3x7qj9g4.execute-api.eu-west-2.amazonaws.com/v1"
    JEKYLL_API_KEY         = "plTBNe7lT95DmuPMyBm2w8bK4cMbwIQk4ci547Kc"
  }
}


resource "aws_amplify_app" "site-arcane-scripts-net" {
  name = "site-arcane-scripts.net"

  environment_variables = {
    "_LIVE_UPDATES" = jsonencode(
      [
        {
          name    = "Jekyll"
          pkg     = "jekyll"
          type    = "ruby"
          version = "4.3.2"
        },
        {
          name    = "Bundler"
          pkg     = "bundler"
          type    = "ruby"
          version = "2.3"
        },
      ]
    )

    JEKYLL_API_KEY                                 = "DEFAULT_VALUE_FROM_TERRAFORM"
    JEKYLL_API_GATEWAY_URL                         = "DEFAULT_VALUE_FROM_TERRAFORM"
    "JEKYLL_API_INVOKE_URL_${terraform.workspace}" = aws_api_gateway_stage.v1.invoke_url
  }

  repository = "https://github.com/chizmw/site-arcane-scripts.net"

  custom_rule {
    source = "https://arcane-scripts.net"
    status = "302"
    target = "https://www.arcane-scripts.net"
  }
  custom_rule {
    source = "/<*>"
    status = "404-200"
    target = "/index.html"
  }
}
