import os
from typing import Optional

# S3 버킷 설정
S3_BUCKET: str = os.getenv('S3_BUCKET', 'crypto-signal-platform-jiny')

# 업비트 API 설정
UPBIT_BASE_URL: str = "https://api.upbit.com/v1"
DEFAULT_MARKET: str = "KRW-BTC"

# Alternative.me API 설정
FEAR_GREED_API_URL: str = "https://api.alternative.me/fng/"

# 데이터 수집 설정
DAILY_DATA_COUNT: int = 365  # 일봉 데이터 개수 (1년치)
MINUTE_DATA_DAYS: int = 30   # 5분봉 데이터 일수 (한달치)

# API 호출 제한 설정
API_REQUEST_DELAY: float = 0.1  # API 호출 간 대기시간 (초)

def get_s3_path(data_type: str, year: int, month: str, day: str, hour: Optional[str] = None, minute: Optional[str] = None) -> str:
    """S3 경로를 생성하는 헬퍼 함수"""
    base_path = f"s3://{S3_BUCKET}/data/{data_type}"
    
    if data_type == "daily_market_data":
        return f"{base_path}/year={year}/month={month}/day={day}/data.parquet"
    elif data_type == "market_5m" and hour and minute:
        return f"{base_path}/year={year}/month={month}/day={day}/hour={hour}/minute={minute}/data.parquet"
    elif data_type == "fear_and_greed_index":
        return f"{base_path}/year={year}/month={month}/day={day}/data.parquet"
    else:
        raise ValueError(f"지원하지 않는 데이터 타입: {data_type}")
