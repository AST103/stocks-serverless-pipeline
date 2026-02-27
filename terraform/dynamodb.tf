# Create the table
resource "aws_dynamodb_table" "stock_winners" {
  name           = "stock-winners"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "date"

  attribute {
    name = "date"
    type = "S"
  }

  # schemaless so we don't need to define the other attributes (ticker, price, etc.) here
}