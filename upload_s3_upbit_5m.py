import requests
import pandas as pd
import datetime
from config import UPBIT_BASE_URL, DEFAULT_MARKET, get_s3_path

# 1. 업비트에서 5분봉 데이터 가져오기
url = f"{UPBIT_BASE_URL}/candles/minutes/5"
params = {"market": DEFAULT_MARKET, "count": 1}  # 최신 1개 5분 캔들만
response = requests.get(url, params=params)
data = response.json()

# 2. Pandas DataFrame으로 변환
df = pd.DataFrame(data)
# 필요한 컬럼만 선택하고, 날짜 형식 변환
df = df[['candle_date_time_kst', 'opening_price', 'high_price', 'low_price', 'trade_price', 'candle_acc_trade_volume']]
df['candle_date_time_kst'] = pd.to_datetime(df['candle_date_time_kst'])

# 3. 최신 5분봉 데이터만 선택 (5분마다 실행 가정)
latest_data = df.iloc[0]
dt = latest_data['candle_date_time_kst']
year = dt.year
month = str(dt.month).zfill(2)
day = str(dt.day).zfill(2)
hour = str(dt.hour).zfill(2)

# 4. S3에 Parquet 형식으로 저장
# DataFrame을 한 줄짜리로 다시 만듭니다.
latest_df = pd.DataFrame([latest_data])

# S3 경로를 시간 단위 파티션에 맞게 구성 (분 단위 제거)
s3_path = get_s3_path("market_5m", year, month, day, hour)

# to_parquet 함수를 사용. s3fs 라이브러리가 설치되어 있으면 바로 S3에 저장이 가능합니다.
latest_df.to_parquet(s3_path, engine='pyarrow', index=False)

print(f"성공적으로 {s3_path}에 데이터를 저장했습니다.")