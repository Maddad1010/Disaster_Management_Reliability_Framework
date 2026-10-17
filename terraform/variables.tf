variable "aws_region" {
  description = "AWS region for all infrastructure"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project resource name prefix"
  type        = string
  default     = "disaster-management"
}

variable "ec2_key_name" {
  description = "Existing AWS EC2 key pair name in ap-south-1"
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "Public IP CIDR allowed to SSH to EC2"
  type        = string
}

variable "app_allowed_cidr" {
  description = "CIDR allowed to access the application"
  type        = string
  default     = "0.0.0.0/0"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}