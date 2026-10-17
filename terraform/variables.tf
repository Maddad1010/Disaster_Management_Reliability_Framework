variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "ap-south-1"
}

variable "ec2_key_name" {
  description = "Existing AWS EC2 key pair name"
  type        = string
  default     = "disaster-management-key"
}

variable "ssh_allowed_cidr" {
  description = "Public IP CIDR allowed to connect over SSH"
  type        = string
  default     = "103.134.130.254/32"
}

variable "app_allowed_cidr" {
  description = "CIDR allowed to access application port 5000"
  type        = string
  default     = "0.0.0.0/0"
}