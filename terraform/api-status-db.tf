# create an aws dynamodb table
resource "aws_dynamodb_table" "api_stat" {
  name         = "api_status-${terraform.workspace}"
  hash_key     = "CallID"
  billing_mode = "PAY_PER_REQUEST"


  attribute {
    name = "CallID"
    type = "S"
  }
  attribute {

    name = "Status"
    type = "S"
  }

  global_secondary_index {
    name            = "StatusIndex"
    hash_key        = "Status"
    projection_type = "ALL"
  }
}
