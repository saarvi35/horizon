output "rds_endpoint" {
  description = "Connection endpoint for AWS RDS MySQL"
  value       = aws_db_instance.mysql_rds.endpoint
}

output "s3_bucket_name" {
  description = "Name of the provisioned S3 Bucket"
  value       = aws_s3_bucket.media_bucket.id
}