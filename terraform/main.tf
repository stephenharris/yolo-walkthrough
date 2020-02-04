provider "aws" {
  region = "eu-west-1"
}

locals{
  training_buckets = [
    "compute-data-f4sy2kau",
    "compute-data-counter-wlw7bxjo",
    "compute-data-spark-digit-ea4a44",
    "compute-data-spark-counter-7gpdf3"
  ]
  key_pair_name="spark-test"
  vpc_id="vpc-30a0b154"
  subnet_id=null
  acccountId = "632192019977"
  region        = "eu-west-1"
  inference_source_bucket_name = "yolo-amr-inference-data-source"
}
