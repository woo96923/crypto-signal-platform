# 1. 베이스 이미지 선택 (가벼운 Python 3.10)
FROM python:3.10-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. AWS CLI 설치 (S3/Athena 접근에 필요할 수 있음)
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws

# 4. 의존성 설치 (효율적인 캐싱을 위해 코드 복사 전에 실행)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 프로젝트 코드 복사
# (만약 스크립트가 여러 폴더에 있다면 'COPY . .' 사용)
COPY ./run_pipeline.py . 
# COPY ./utils/ /app/utils/

# 6. 컨테이너가 실행될 때 수행할 기본 명령어
# (run_pipeline.py 스크립트를 실행하도록 설정)
CMD ["python", "run_pipeline.py"]