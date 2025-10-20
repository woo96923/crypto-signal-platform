import requests
import pandas as pd
from datetime import datetime
from config import FEAR_GREED_API_URL, get_s3_path

# 1. Alternative.me API에서 데이터 가져오기
response = requests.get(f"{FEAR_GREED_API_URL}?limit=1")
data = response.json()['data'][0]

# 2. Pandas DataFrame으로 변환
df = pd.DataFrame([data])
# 문자열 -> 숫자 캐스팅 후 초 단위로 datetime 변환 (경고 및 호환성 OK)
df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp'], errors='coerce'), unit='s')

# 3. S3 경로 파티션 설정
dt = datetime.now()
year = dt.year
month = str(dt.month).zfill(2)
day = str(dt.day).zfill(2)

# 4. S3에 Parquet 형식으로 저장
s3_path = get_s3_path("fear_and_greed_index", year, month, day)
df.to_parquet(s3_path, engine='pyarrow', index=False)

print(f"성공적으로 {s3_path}에 데이터를 저장했습니다.")