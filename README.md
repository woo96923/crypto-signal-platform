# Crypto Signal Platform

암호화폐 시장 데이터를 수집하고 S3에 저장하는 플랫폼입니다.

## 기능

- **일봉 데이터 수집**: 업비트에서 일봉 데이터를 수집하여 S3에 저장
- **5분봉 데이터 수집**: 업비트에서 5분봉 데이터를 수집하여 S3에 저장  
- **Fear & Greed Index 수집**: Alternative.me API에서 공포탐욕지수를 수집하여 S3에 저장
- **초기 데이터 수집**: 일봉 1년치, 5분봉 한달치 데이터를 한번에 수집

## 설치

1. 가상환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

3. 환경변수 설정:
```bash
cp env.example .env
# .env 파일을 편집하여 실제 S3 버킷명 입력
```

## 사용법

### 초기 데이터 수집 (한번만 실행)
```bash
python init_data_collection.py
```

### 정기 데이터 수집
- **일봉 데이터**: 매일 실행
```bash
python upload_s3_upbit.py
```

- **Fear & Greed Index**: 매일 실행
```bash
python upload_s3_feargreed.py
```

### 크론 작업 설정 예시
```bash
# 매일 오전 9시에 일봉 데이터 수집
0 9 * * * /path/to/venv/bin/python /path/to/upload_s3_upbit.py

# 매일 오전 9시 5분에 Fear & Greed Index 수집
5 9 * * * /path/to/venv/bin/python /path/to/upload_s3_feargreed.py
```

## 환경변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `S3_BUCKET` | AWS S3 버킷명 | `crypto-signal-platform-jiny` |
| `AWS_ACCESS_KEY_ID` | AWS 액세스 키 (선택사항) | - |
| `AWS_SECRET_ACCESS_KEY` | AWS 시크릿 키 (선택사항) | - |
| `AWS_DEFAULT_REGION` | AWS 리전 | `ap-northeast-2` |

## S3 데이터 구조

```
s3://your-bucket/
├── data/
│   ├── daily_market_data/
│   │   └── year=2024/month=01/day=15/data.parquet
│   ├── market_5m/
│   │   └── year=2024/month=01/day=15/hour=09/minute=30/data.parquet
│   └── fear_and_greed_index/
│       └── year=2024/month=01/day=15/data.parquet
```

## 보안

- 민감한 정보는 환경변수로 관리
- `.env` 파일은 `.gitignore`에 포함되어 Git에 커밋되지 않음
- AWS 자격증명은 AWS CLI나 IAM 역할 사용 권장

## 라이선스

MIT License
