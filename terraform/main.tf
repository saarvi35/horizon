# Security Group for Database
resource "aws_security_group" "rds_sg" {
  name        = "horizon-rds-sg"
  description = "Allow MySQL traffic from K8s cluster"

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"] # Restricted to internal VPC CIDR
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "horizon-rds-sg"
    Environment = var.environment
  }
}

# Managed AWS RDS MySQL Database Instance
resource "aws_db_instance" "mysql_rds" {
  allocated_storage      = 20
  max_allocated_storage  = 100
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.t2.micro" 
  db_name                = var.db_name
  username               = var.db_user
  password               = var.db_password
  parameter_group_name   = "default.mysql8.0"
  skip_final_snapshot    = true
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  tags = {
    Name        = "horizon-mysql-rds"
    Environment = var.environment
  }
}

# AWS S3 Bucket for Media Storage
resource "aws_s3_bucket" "media_bucket" {
  bucket        = "horizon-media-assets-${var.environment}"
  force_destroy = false

  tags = {
    Name        = "horizon-media-bucket"
    Environment = var.environment
  }
}

# Enable S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "media_versioning" {
  bucket = aws_s3_bucket.media_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}