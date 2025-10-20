import requests
import pandas as pd
import datetime
import time
from typing import List, Dict
from config import S3_BUCKET, UPBIT_BASE_URL, DEFAULT_MARKET, DAILY_DATA_COUNT, MINUTE_DATA_DAYS, API_REQUEST_DELAY, get_s3_path

def get_daily_data(market: str = DEFAULT_MARKET, count: int = DAILY_DATA_COUNT) -> pd.DataFrame:
    """일봉 데이터를 가져오는 함수"""
    print(f"📊 일봉 데이터 {count}개 가져오는 중...")
    
    url = f"{UPBIT_BASE_URL}/candles/days"
    params = {"market": market, "count": count}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        df = pd.DataFrame(data)
        df = df[['candle_date_time_kst', 'opening_price', 'high_price', 'low_price', 'trade_price', 'candle_acc_trade_volume']]
        df['candle_date_time_kst'] = pd.to_datetime(df['candle_date_time_kst'])
        
        print(f"✅ 일봉 데이터 {len(df)}개 수집 완료")
        return df
        
    except Exception as e:
        print(f"❌ 일봉 데이터 수집 실패: {e}")
        return pd.DataFrame()

def get_5min_data(market: str = DEFAULT_MARKET, days: int = MINUTE_DATA_DAYS) -> pd.DataFrame:
    """5분봉 데이터를 가져오는 함수 (한달치)"""
    print(f"📊 5분봉 데이터 {days}일치 가져오는 중...")
    
    # 한달치 5분봉 데이터는 약 8,640개 (30일 * 24시간 * 12개/시간)
    # API 제한으로 인해 여러 번 요청해야 함
    url = f"{UPBIT_BASE_URL}/candles/minutes/5"
    all_data = []
    
    # 최대 200개씩 가져올 수 있으므로 여러 번 요청
    total_requests = (days * 24 * 12) // 200 + 1
    
    for i in range(total_requests):
        try:
            params = {"market": market, "count": 200}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
                
            all_data.extend(data)
            
            # 마지막 캔들의 시간을 기준으로 다음 요청을 위한 시간 설정
            if data:
                last_time = data[-1]['candle_date_time_kst']
                # 다음 요청을 위해 시간 파라미터 추가
                params['to'] = last_time
            
            print(f"  진행률: {i+1}/{total_requests} (수집된 데이터: {len(all_data)}개)")
            
            # API 호출 제한을 위한 대기
            time.sleep(API_REQUEST_DELAY)
            
        except Exception as e:
            print(f"❌ 5분봉 데이터 수집 중 오류 (요청 {i+1}): {e}")
            break
    
    if all_data:
        df = pd.DataFrame(all_data)
        df = df[['candle_date_time_kst', 'opening_price', 'high_price', 'low_price', 'trade_price', 'candle_acc_trade_volume']]
        df['candle_date_time_kst'] = pd.to_datetime(df['candle_date_time_kst'])
        
        # 중복 제거 및 정렬
        df = df.drop_duplicates(subset=['candle_date_time_kst']).sort_values('candle_date_time_kst')
        
        print(f"✅ 5분봉 데이터 {len(df)}개 수집 완료")
        return df
    else:
        print("❌ 5분봉 데이터 수집 실패")
        return pd.DataFrame()

def save_daily_data_to_s3(df: pd.DataFrame):
    """일봉 데이터를 S3에 저장"""
    print("💾 일봉 데이터 S3 저장 중...")
    
    for _, row in df.iterrows():
        dt = row['candle_date_time_kst']
        year = dt.year
        month = str(dt.month).zfill(2)
        day = str(dt.day).zfill(2)
        
        # DataFrame을 한 줄짜리로 만들기
        single_row_df = pd.DataFrame([row])
        
        # S3 경로 구성
        s3_path = get_s3_path("daily_market_data", year, month, day)
        
        try:
            single_row_df.to_parquet(s3_path, engine='pyarrow', index=False)
            print(f"  저장됨: {dt.strftime('%Y-%m-%d')}")
        except Exception as e:
            print(f"❌ 저장 실패 ({dt.strftime('%Y-%m-%d')}): {e}")

def save_5min_data_to_s3(df: pd.DataFrame):
    """5분봉 데이터를 S3에 저장"""
    print("💾 5분봉 데이터 S3 저장 중...")
    
    saved_count = 0
    for _, row in df.iterrows():
        dt = row['candle_date_time_kst']
        year = dt.year
        month = str(dt.month).zfill(2)
        day = str(dt.day).zfill(2)
        hour = str(dt.hour).zfill(2)
        minute = str(dt.minute).zfill(2)
        
        # DataFrame을 한 줄짜리로 만들기
        single_row_df = pd.DataFrame([row])
        
        # S3 경로 구성
        s3_path = get_s3_path("market_5m", year, month, day, hour, minute)
        
        try:
            single_row_df.to_parquet(s3_path, engine='pyarrow', index=False)
            saved_count += 1
            
            # 진행률 출력 (100개마다)
            if saved_count % 100 == 0:
                print(f"  저장 진행률: {saved_count}/{len(df)} ({saved_count/len(df)*100:.1f}%)")
                
        except Exception as e:
            print(f"❌ 저장 실패 ({dt.strftime('%Y-%m-%d %H:%M')}): {e}")
    
    print(f"✅ 5분봉 데이터 저장 완료: {saved_count}/{len(df)}개")

def main():
    """메인 실행 함수"""
    print("🚀 초기 데이터 수집 시작")
    print("=" * 50)
    
    # 1. 일봉 데이터 수집 및 저장 (1년치)
    print("\n📅 일봉 데이터 수집 (1년치)")
    daily_df = get_daily_data(count=DAILY_DATA_COUNT)
    if not daily_df.empty:
        save_daily_data_to_s3(daily_df)
    
    print("\n" + "=" * 50)
    
    # 2. 5분봉 데이터 수집 및 저장 (한달치)
    print("\n⏰ 5분봉 데이터 수집 (한달치)")
    min5_df = get_5min_data(days=MINUTE_DATA_DAYS)
    if not min5_df.empty:
        save_5min_data_to_s3(min5_df)
    
    print("\n" + "=" * 50)
    print("🎉 초기 데이터 수집 완료!")
    print(f"일봉 데이터: {len(daily_df)}개")
    print(f"5분봉 데이터: {len(min5_df)}개")

if __name__ == "__main__":
    main()
