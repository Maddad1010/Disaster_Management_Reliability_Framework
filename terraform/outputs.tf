
output "ec2_instance_id" {
  value = aws_instance.lab_instance.id
}

output "ec2_public_ip" {
  value = aws_instance.lab_instance.public_ip
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "application_url" {
  value = "http://${aws_instance.lab_instance.public_ip}:5000"
}
