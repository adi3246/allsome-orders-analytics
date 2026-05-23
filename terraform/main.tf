# =============================================================================
# Terraform Configuration - Allsome Orders Analytics
#
# Provisions AWS infrastructure for the application:
# - Security Group: Allows HTTP (80), HTTPS (443), and SSH (22) access
# - EC2 Instance: Runs Docker containers (backend, frontend, database)
# - Elastic IP: Provides a stable public IP address
#
# Usage:
#   terraform init
#   terraform plan -var="key_pair_name=my-key" -var="db_password=secret"
#   terraform apply
# =============================================================================

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Security group for the EC2 instance
# Allows inbound HTTP/HTTPS from anywhere and SSH from specified CIDRs
resource "aws_security_group" "app_sg" {
  name        = "${var.project_name}-sg"
  description = "Security group for Allsome Orders Analytics"

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidr
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "${var.project_name}-sg"
    Project = var.project_name
  }
}

# EC2 instance - runs Docker containers for the full application stack
# Bootstrapped via user_data.sh which installs Docker and prepares the environment
resource "aws_instance" "app_server" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  user_data = templatefile("${path.module}/user_data.sh", {
    db_password     = var.db_password
    github_repo_url = var.github_repo_url
  })

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = {
    Name    = "${var.project_name}-server"
    Project = var.project_name
  }
}

# Elastic IP for stable public address
resource "aws_eip" "app_eip" {
  instance = aws_instance.app_server.id
  domain   = "vpc"

  tags = {
    Name    = "${var.project_name}-eip"
    Project = var.project_name
  }
}
