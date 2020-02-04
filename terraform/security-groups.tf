resource "aws_security_group" "compute_instance_security_group" {
  name        = "compute_instance_security_group"
  description = "Access to security group"
  vpc_id      = local.vpc_id
}

resource "aws_security_group_rule" "ssh_access_spark" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  description       = "SSH access from Spark IP addresses"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.compute_instance_security_group.id
}

resource "aws_security_group_rule" "outbound_allow_all" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  description       = "Outbound allow all"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.compute_instance_security_group.id
}
