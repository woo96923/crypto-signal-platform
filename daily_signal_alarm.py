#!/usr/bin/env python3
"""
매일 9시에 실행되는 비트코인 매매 시그널 알람 스크립트 (S3 기반)
크론 작업으로 설정하여 자동 실행
데이터 수집이 완료된 후 실행되도록 설계
"""

import sys
import os
from datetime import datetime
from crypto_signal_analyzer_s3 import CryptoSignalAnalyzerS3

def main():
    """매일 실행되는 메인 함수"""
    print(f"🕘 매매 시그널 알람 실행 (S3 기반) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 시그널 분석기 초기화 (S3 기반)
        analyzer = CryptoSignalAnalyzerS3()
        
        # 시그널 분석 실행
        analysis = analyzer.analyze_trading_signal()
        
        if 'error' in analysis:
            print(f"❌ 분석 실패: {analysis['error']}")
            sys.exit(1)
        
        # 리포트 출력
        analyzer.print_signal_report(analysis)
        
        # 강한 시그널이 있을 때만 추가 알람
        signal = analysis['trading_signal']
        if signal['strength'] == '강함':
            print(f"\n🔥 강한 시그널 감지! 즉시 확인 필요!")
            print(f"   신호: {signal['signal']}")
            print(f"   이유: {signal['reason']}")
        
        print(f"\n✅ 시그널 분석 완료 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
