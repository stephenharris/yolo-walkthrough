resource "aws_s3_bucket" "training_bucket" {
  count = length(local.training_buckets)
  bucket = local.training_buckets[count.index]
  acl    = "private"
  lifecycle {
    prevent_destroy = false
  }
  versioning {
    enabled = true
  }
}