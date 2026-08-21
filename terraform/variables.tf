variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "production"
}

variable "db_name" {
  description = "Name of the MySQL database"
  type        = string
  default     = "beleva"
}

variable "db_user" {
  description = "Username for database"
  type        = string
  default     = "horizon_user"
}

variable "db_password" {
  description = "Password for database"
  type        = string
  sensitive   = true
}