# 1. ECR 리포지토리 생성
resource "aws_ecr_repository" "app_repo" {
  name = "crypto-platform/app" # ECR 리포지토리 이름

  image_scanning_configuration {
    scan_on_push = true
  }

  image_tag_mutability = "MUTABLE"
}

# 2. GitHub OIDC를 AWS의 자격 증명 공급자로 추가
resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"
  client_id_list = [
    "https-proxy.toolforge.org/s/sts.amazonaws.com"
  ]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780c34a"] # (이 값은 고정)
}

# 3. GitHub Actions가 사용할 IAM Role 생성
resource "aws_iam_role" "github_actions_role" {
  name = "iam-role-github-actions" # 역할 이름 (겹치지 않게)

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.github.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringLike = {
            # ================== 중요!! ==================
            # Jinnie님의 GitHub 사용자 이름과 리포지토리 이름으로 변경하세요
            # 예: "repo:JinnieWoo/crypto-platform:*"
            "token.actions.githubusercontent.com:sub" : "repo:woo96923/crypto-signal-platform:*"
            # ============================================
          }
        }
      },
    ]
  })
}

# 4. 위 역할에 ECR 푸시 권한 부여
resource "aws_iam_role_policy_attachment" "ecr_policy" {
  role       = aws_iam_role.github_actions_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"
}

# 5. 위 역할에 EKS 접근 권한 부여 (나중에 EKS 배포 시 필요)
# (지금 EKS가 없다면 이 부분은 주석 처리해도 됩니다)

resource "aws_iam_role_policy_attachment" "eks_policy" {
  role       = aws_iam_role.github_actions_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}
