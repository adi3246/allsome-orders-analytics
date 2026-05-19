output "public_ip" {
  description = "Public IP address of the application server"
  value       = aws_eip.app_eip.public_ip
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.app_server.id
}

output "app_url" {
  description = "Application URL"
  value       = "http://${aws_eip.app_eip.public_ip}"
}
