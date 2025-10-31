# 1. 베이스 이미지 선택 (가벼운 Python 3.10)
FROM python:3.10-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. AWS CLI 설치
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws

# 4. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 프로젝트의 모든 Python 코드 및 설정 복사 (만능 툴박스)
COPY ./*.py ./
COPY ./config.py ./

# 6. CMD 제거: 실행 명령은 Kubernetes 매니페스트에서 지정
