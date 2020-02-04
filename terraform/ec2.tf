resource "aws_instance" "compute_instance" {
  ami           = "ami-078d068af898f9114"
  instance_type = "p2.xlarge"
  timeouts {
    create = "20m"
  }
  monitoring = false
  disable_api_termination = false

  vpc_security_group_ids = [
    aws_security_group.compute_instance_security_group.id
  ]
  subnet_id = local.subnet_id
  key_name = local.key_pair_name
  iam_instance_profile = aws_iam_instance_profile.compute_profile.name 
  ebs_optimized = true
  root_block_device {
    volume_type = "gp2"
    volume_size = "95"
  }
  tags = {
    Name = "Compute"
  }
}

resource "aws_iam_instance_profile" "compute_profile" {
  name = "Compute-InstanceRoleInstanceProfile-UT8B0E1Q"
  role = aws_iam_role.compute_role.name
}

resource "aws_iam_role" "compute_role" {
  name = "Compute-InstanceRole-51MJSE1A"

  assume_role_policy = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "compute_role_policy" {
    name = "InstanceRole"
    role = aws_iam_role.compute_role.id
    policy = data.aws_iam_policy_document.instance_role_policy.json
}

data "aws_iam_policy_document" "instance_role_policy" {
  statement {
    effect = "Allow"
    
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:ListBucket",
      "s3:DeleteObject"
    ]

    resources = concat(
      formatlist("arn:aws:s3:::%s", local.training_buckets),
      formatlist("arn:aws:s3:::%s/*", local.training_buckets)
    )
  }
}