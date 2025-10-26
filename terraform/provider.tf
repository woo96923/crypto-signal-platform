terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0" # AWS 프로바이더 버전 지정
    }
  }
}

# 어떤 리전에서 작업할지 기본값 설정
provider "aws" {
  region = "ap-northeast-2" # 서울 리전
}