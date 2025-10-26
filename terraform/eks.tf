# 1. EKS가 사용할 VPC (네트워크) 생성
# AWS에서 가장 표준으로 사용하는 VPC 모듈입니다.
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.5.3" # (2025-10-23 기준 최신 안정화 버전)

  name = "crypto-platform-vpc"
  cidr = "10.0.0.0/16" # VPC가 사용할 IP 대역

  # 서울 리전의 3개 가용 영역에 네트워크를 만듭니다.
  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true  # 프라이빗 서브넷이 인터넷에 나갈 수 있게 (필수)
  single_nat_gateway = true  # 비용 절약을 위해 NAT 게이트웨이는 1개만
  enable_dns_hostnames = true

  # 쿠버네티스가 로드밸런서를 만들 때 필요한 태그
  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb"                  = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb"         = "1"
  }
}

# 2. EKS 클러스터 생성 (Control Plane + Worker Nodes)
# AWS에서 가장 표준으로 사용하는 EKS 모듈입니다.
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "20.8.4" # (2025-10-23 기준 최신 안정화 버전)

  cluster_name    = var.cluster_name
  cluster_version = "1.29" # 쿠버네티스 버전

  # 1번에서 만든 VPC 정보를 EKS에 연결합니다.
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # EKS 워커 노드(EC2) 그룹 설정
  eks_managed_node_groups = {
    main = {
      name           = "main-node-group"
      instance_types = ["t3.medium"] # 🚨 프리티어가 아니므로 비용 발생!
      min_size     = 1 # 최소 1대
      max_size     = 3 # 최대 3대
      desired_size = 2 # 평소 2대
    }
  }
}