# create a secret in AWS Secrets Manager
# with a DUMMY value that we don't mind if it changes
# so we can manage the secret's existence here, but set the value manually when
# we need to
resource "aws_secretsmanager_secret" "discord_webhook_secret" {
  name = "${local.pdf_api_name}/discord-webhook-url/${local.api_stage}"
}
