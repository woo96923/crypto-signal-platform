import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import s3fs
from config import S3_BUCKET, FEAR_GREED_API_URL

class CryptoSignalAnalyzerS3:
    """S3 데이터를 활용한 암호화폐 매매 시그널 분석기"""
    
    def __init__(self, market: str = "KRW-BTC"):
        self.market = market
        self.short_ma_period = 60  # 60일 이동평균
        self.long_ma_period = 120   # 120일 이동평균
        self.s3 = s3fs.S3FileSystem()
        
    def get_daily_data_from_s3(self, days: int = 200) -> pd.DataFrame:
        """S3에서 일봉 데이터 가져오기"""
        try:
            print(f"📊 S3에서 최근 {days}일치 일봉 데이터 수집 중...")
            
            # 최근 날짜부터 역순으로 데이터 수집
            end_date = datetime.now()
            all_data = []
            
            for i in range(days):
                current_date = end_date - timedelta(days=i)
                year = current_date.year
                month = str(current_date.month).zfill(2)
                day = str(current_date.day).zfill(2)
                
                s3_path = f"s3://{S3_BUCKET}/data/daily_market_data/year={year}/month={month}/day={day}/data.parquet"
                
                try:
                    if self.s3.exists(s3_path):
                        df = pd.read_parquet(s3_path)
                        all_data.append(df)
                        print(f"  ✅ {current_date.strftime('%Y-%m-%d')} 데이터 로드")
                    else:
                        print(f"  ⚠️ {current_date.strftime('%Y-%m-%d')} 데이터 없음")
                except Exception as e:
                    print(f"  ❌ {current_date.strftime('%Y-%m-%d')} 로드 실패: {e}")
            
            if not all_data:
                print("❌ S3에서 일봉 데이터를 찾을 수 없습니다.")
                return pd.DataFrame()
            
            # 모든 데이터 합치기
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_df['candle_date_time_kst'] = pd.to_datetime(combined_df['candle_date_time_kst'])
            
            # 시간순으로 정렬 (오래된 것부터)
            combined_df = combined_df.sort_values('candle_date_time_kst').reset_index(drop=True)
            
            print(f"✅ 총 {len(combined_df)}개 일봉 데이터 수집 완료")
            return combined_df
            
        except Exception as e:
            print(f"❌ S3 일봉 데이터 수집 실패: {e}")
            return pd.DataFrame()
    
    def get_fear_greed_from_s3(self) -> Dict:
        """S3에서 공포탐욕지수 데이터 가져오기"""
        try:
            print("📊 S3에서 공포탐욕지수 데이터 수집 중...")
            
            # 오늘 날짜의 공포탐욕지수 데이터 가져오기
            today = datetime.now()
            year = today.year
            month = str(today.month).zfill(2)
            day = str(today.day).zfill(2)
            
            s3_path = f"s3://{S3_BUCKET}/data/fear_and_greed_index/year={year}/month={month}/day={day}/data.parquet"
            
            if self.s3.exists(s3_path):
                df = pd.read_parquet(s3_path)
                if not df.empty:
                    data = df.iloc[0]
                    return {
                        "value": int(data['value']),
                        "classification": data['value_classification'],
                        "timestamp": data['timestamp']
                    }
            
            print("⚠️ 오늘의 공포탐욕지수 데이터가 없습니다. API에서 직접 가져옵니다.")
            return self._get_fear_greed_from_api()
            
        except Exception as e:
            print(f"❌ S3 공포탐욕지수 수집 실패: {e}")
            return self._get_fear_greed_from_api()
    
    def _get_fear_greed_from_api(self) -> Dict:
        """API에서 공포탐욕지수 직접 가져오기 (백업용)"""
        try:
            import requests
            response = requests.get(f"{FEAR_GREED_API_URL}?limit=1")
            response.raise_for_status()
            data = response.json()['data'][0]
            
            return {
                "value": int(data['value']),
                "classification": data['value_classification'],
                "timestamp": data['timestamp']
            }
            
        except Exception as e:
            print(f"❌ API 공포탐욕지수 수집 실패: {e}")
            return {"value": None, "classification": "Unknown", "timestamp": None}
    
    def calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """이동평균선 계산"""
        if df.empty:
            return df
            
        # 종가 기준으로 이동평균 계산
        df['ma_60'] = df['trade_price'].rolling(window=self.short_ma_period).mean()
        df['ma_120'] = df['trade_price'].rolling(window=self.long_ma_period).mean()
        
        return df
    
    def detect_cross_signals(self, df: pd.DataFrame) -> Dict:
        """골든크로스/데드크로스 감지"""
        if len(df) < 2:
            return {"signal": "데이터 부족", "type": None, "strength": None}
        
        # 최신 2일 데이터로 크로스 감지
        latest = df.iloc[-1]
        previous = df.iloc[-2]
        
        # 이동평균선이 모두 존재하는지 확인
        if pd.isna(latest['ma_60']) or pd.isna(latest['ma_120']) or pd.isna(previous['ma_60']) or pd.isna(previous['ma_120']):
            return {"signal": "이동평균선 데이터 부족", "type": None, "strength": None}
        
        # 골든크로스: 60일선이 120일선을 위로 돌파
        if (previous['ma_60'] <= previous['ma_120']) and (latest['ma_60'] > latest['ma_120']):
            return {
                "signal": "골든크로스",
                "type": "golden_cross",
                "strength": "강한 매수 신호",
                "ma_60": latest['ma_60'],
                "ma_120": latest['ma_120']
            }
        
        # 데드크로스: 60일선이 120일선을 아래로 이탈
        elif (previous['ma_60'] >= previous['ma_120']) and (latest['ma_60'] < latest['ma_120']):
            return {
                "signal": "데드크로스",
                "type": "dead_cross",
                "strength": "강한 매도 신호",
                "ma_60": latest['ma_60'],
                "ma_120": latest['ma_120']
            }
        
        # 현재 상태만 반환
        elif latest['ma_60'] > latest['ma_120']:
            return {
                "signal": "골든크로스 상태 유지",
                "type": "golden_cross_state",
                "strength": None,
                "ma_60": latest['ma_60'],
                "ma_120": latest['ma_120']
            }
        else:
            return {
                "signal": "데드크로스 상태 유지",
                "type": "dead_cross_state",
                "strength": None,
                "ma_60": latest['ma_60'],
                "ma_120": latest['ma_120']
            }
    
    def analyze_trading_signal(self) -> Dict:
        """매매 시그널 종합 분석"""
        print("🔍 S3 기반 비트코인 매매 시그널 분석 시작...")
        
        # 1. S3에서 일봉 데이터 수집
        df = self.get_daily_data_from_s3()
        if df.empty:
            return {"error": "S3 일봉 데이터 수집 실패"}
        
        # 2. 이동평균선 계산
        df = self.calculate_moving_averages(df)
        
        # 3. 크로스 신호 감지
        cross_signal = self.detect_cross_signals(df)
        
        # 4. S3에서 공포탐욕지수 수집
        fear_greed = self.get_fear_greed_from_s3()
        
        # 5. 최신 가격 정보
        latest_price = df.iloc[-1]['trade_price']
        latest_date = df.iloc[-1]['candle_date_time_kst']
        
        # 6. 매매 시그널 판단
        trading_signal = self._determine_trading_signal(cross_signal, fear_greed)
        
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "market": self.market,
            "latest_price": latest_price,
            "latest_date": latest_date.strftime("%Y-%m-%d"),
            "cross_signal": cross_signal,
            "fear_greed": fear_greed,
            "trading_signal": trading_signal,
            "data_source": "S3"
        }
    
    def _determine_trading_signal(self, cross_signal: Dict, fear_greed: Dict) -> Dict:
        """매매 시그널 판단 로직"""
        if not fear_greed.get('value'):
            return {"signal": "공포탐욕지수 데이터 없음", "strength": None}
        
        fg_value = fear_greed['value']
        cross_type = cross_signal.get('type')
        
        # 골든크로스 + 공포탐욕지수 조합
        if cross_type in ['golden_cross', 'golden_cross_state']:
            if fg_value <= 20:
                return {
                    "signal": "강한 매수",
                    "strength": "강함",
                    "reason": f"골든크로스 + 극도 공포({fg_value})"
                }
            elif 21 <= fg_value <= 40:
                return {
                    "signal": "보통 매수",
                    "strength": "보통",
                    "reason": f"골든크로스 + 공포({fg_value})"
                }
            else:
                return {
                    "signal": "골든크로스 상태",
                    "strength": "약함",
                    "reason": f"골든크로스 + 탐욕({fg_value})"
                }
        
        # 데드크로스 + 공포탐욕지수 조합
        elif cross_type in ['dead_cross', 'dead_cross_state']:
            if fg_value >= 80:
                return {
                    "signal": "강한 매도",
                    "strength": "강함",
                    "reason": f"데드크로스 + 극도 탐욕({fg_value})"
                }
            elif 60 <= fg_value <= 79:
                return {
                    "signal": "보통 매도",
                    "strength": "보통",
                    "reason": f"데드크로스 + 탐욕({fg_value})"
                }
            else:
                return {
                    "signal": "데드크로스 상태",
                    "strength": "약함",
                    "reason": f"데드크로스 + 공포({fg_value})"
                }
        
        return {
            "signal": "신호 없음",
            "strength": None,
            "reason": "명확한 시그널 없음"
        }
    
    def print_signal_report(self, analysis: Dict):
        """시그널 리포트 출력"""
        print("\n" + "="*60)
        print("📊 비트코인 매매 시그널 리포트 (S3 기반)")
        print("="*60)
        
        print(f"🕐 분석 시간: {analysis['timestamp']}")
        print(f"💰 현재 가격: {analysis['latest_price']:,.0f}원")
        print(f"📅 기준 날짜: {analysis['latest_date']}")
        print(f"📊 데이터 소스: {analysis['data_source']}")
        
        print(f"\n📈 이동평균선 상태:")
        cross = analysis['cross_signal']
        print(f"   • 60일선: {cross.get('ma_60', 0):,.0f}원")
        print(f"   • 120일선: {cross.get('ma_120', 0):,.0f}원")
        print(f"   • 상태: {cross['signal']}")
        
        print(f"\n😨 공포탐욕지수:")
        fg = analysis['fear_greed']
        print(f"   • 지수: {fg['value']}")
        print(f"   • 분류: {fg['classification']}")
        
        print(f"\n🎯 매매 시그널:")
        signal = analysis['trading_signal']
        print(f"   • 신호: {signal['signal']}")
        if signal['strength']:
            print(f"   • 강도: {signal['strength']}")
        print(f"   • 이유: {signal['reason']}")
        
        print("="*60)
        
        # 알람 메시지 생성
        self._generate_alarm_message(analysis)
    
    def _generate_alarm_message(self, analysis: Dict):
        """알람 메시지 생성"""
        signal = analysis['trading_signal']
        fg = analysis['fear_greed']
        cross = analysis['cross_signal']
        
        if signal['strength'] in ['강함', '보통']:
            print(f"\n🚨 알람 메시지:")
            print(f"   {signal['signal']} 신호 발생!")
            print(f"   이유: {signal['reason']}")
            print(f"   현재가: {analysis['latest_price']:,.0f}원")
            print(f"   공포탐욕지수: {fg['value']} ({fg['classification']})")

def main():
    """메인 실행 함수"""
    analyzer = CryptoSignalAnalyzerS3()
    
    try:
        # 시그널 분석 실행
        analysis = analyzer.analyze_trading_signal()
        
        if 'error' in analysis:
            print(f"❌ 분석 실패: {analysis['error']}")
            return
        
        # 리포트 출력
        analyzer.print_signal_report(analysis)
        
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
