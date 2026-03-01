# configuration
variable "aws_region" {
  description = "AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}

variable "massive_api_key" {
  description = "Massive API key for fetching stock data"
  type        = string
  sensitive   = true
}
