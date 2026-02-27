# configuration
variable "aws_region" {
  description = "AWS region to deploy resources in"
  type        = string
  default = "us-east-1"
}

variable "aws_profile" {
  description = "AWS profile to use for deployment"
  type        = string
  default = "default"
}

variable "massive_api_key" {
  description = "Massive API key for fetching stock data"
  type        = string
  sensitive = true
}