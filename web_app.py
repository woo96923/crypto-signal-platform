import json
import streamlit as st
from crypto_signal_analyzer_s3 import CryptoSignalAnalyzerS3


st.set_page_config(page_title="Crypto Signal Analyzer", page_icon="📊", layout="wide")

st.title("📊 Crypto Signal Analyzer (S3 기반)")
st.caption("S3에 저장된 데이터로 비트코인 매매 시그널을 분석합니다.")

with st.sidebar:
    st.header("설정")
    market = st.text_input("마켓 (ex. KRW-BTC)", value="KRW-BTC")
    days = st.slider("최근 일수", min_value=60, max_value=365, value=200, step=10)

analyze = st.button("🔍 분석 실행", type="primary")

if analyze:
    with st.spinner("S3 데이터 로드 및 분석 중..."):
        analyzer = CryptoSignalAnalyzerS3(market=market)
        # 최근 일수는 내부 메소드에서 사용하므로 임시로 속성만 조정
        try:
            analysis = analyzer.analyze_trading_signal()
        except Exception as e:
            st.error(f"분석 중 오류가 발생했습니다: {e}")
            st.stop()

    if "error" in analysis:
        st.error(analysis["error"])
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("요약")
            st.metric(label="현재가", value=f"{int(analysis['latest_price']):,} 원")
            st.write(f"기준 날짜: {analysis['latest_date']}")
            st.write(f"마켓: {analysis['market']}")
            st.write(f"데이터 소스: {analysis['data_source']}")

        with col2:
            st.subheader("매매 시그널")
            signal = analysis["trading_signal"]
            st.write(f"신호: {signal['signal']}")
            if signal.get("strength"):
                st.write(f"강도: {signal['strength']}")
            st.write(f"이유: {signal.get('reason', '-')}")

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("이동평균선 상태")
            cross = analysis["cross_signal"]
            st.json({
                "ma_60": cross.get("ma_60"),
                "ma_120": cross.get("ma_120"),
                "상태": cross.get("signal"),
                "타입": cross.get("type"),
            })

        with c2:
            st.subheader("공포탐욕지수")
            st.json(analysis["fear_greed"])

        st.divider()
        st.subheader("원시 분석 데이터")
        st.json(analysis)


