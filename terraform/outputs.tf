output "ec2_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.app.public_ip
}

output "ecr_repository_url" {
  description = "URL of the existing ECR repository"
  value       = data.aws_ecr_repository.app.repository_url
}

output "ec2_instance_id" {
  description = "ID of the created EC2 instance"
  value       = aws_instance.app.id
}