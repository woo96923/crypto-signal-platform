variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-2"
}

# EKS 클러스터 이름을 변수로 관리
variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "crypto-platform-eks"
}