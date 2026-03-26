import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="Global Stock Analyzer", layout="wide")

st.title("📈 한-미 주요 주식 수익률 비교 분석")
st.sidebar.header("설정")

# 1. 사이드바 - 분석 대상 설정
# 한국 주식은 .KS(코스피) 또는 .KQ(코스닥)를 붙여야 합니다.
default_tickers = "AAPL, TSLA, 005930.KS, 000660.KS"
tickers_input = st.sidebar.text_input("주식 티커 입력 (쉼표로 구분)", default_tickers)
tickers = [t.strip().upper() for t in tickers_input.split(",")]

# 날짜 선택
start_date = st.sidebar.date_input("시작 날짜", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("종료 날짜", datetime.now())

if st.sidebar.button("데이터 불러오기"):
    try:
        # 데이터 다운로드
        data = yf.download(tickers, start=start_date, end=end_date)['Close']
        
        if data.empty:
            st.error("데이터를 불러올 수 없습니다. 티커를 확인해주세요.")
        else:
            # 2. 수익률 계산 (누적 수익률)
            # 첫 번째 행의 값으로 나누어 100을 기준으로 정규화
            returns = (data / data.iloc[0] - 1) * 100

            # 3. 레이아웃 구성
            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("📊 누적 수익률 비교 (%)")
                fig = go.Figure()
                for ticker in returns.columns:
                    fig.add_trace(go.Scatter(x=returns.index, y=returns[ticker], name=ticker))
                
                fig.update_layout(
                    xaxis_title="날짜",
                    yaxis_title="수익률 (%)",
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("📋 주요 통계")
                summary = pd.DataFrame({
                    "현재가": data.iloc[-1],
                    "기간 수익률(%)": returns.iloc[-1]
                }).sort_values(by="기간 수익률(%)", ascending=False)
                
                st.table(summary.style.format("{:.2f}"))

            # 4. 개별 주가 차트 (멀티 셀렉트)
            st.divider()
            selected_ticker = st.selectbox("상세 차트를 볼 종목 선택", tickers)
            
            if selected_ticker:
                ticker_data = yf.Ticker(selected_ticker).history(start=start_date, end=end_date)
                fig_candle = go.Figure(data=[go.Candlestick(
                    x=ticker_data.index,
                    open=ticker_data['Open'],
                    high=ticker_data['High'],
                    low=ticker_data['Low'],
                    close=ticker_data['Close'],
                    name=selected_ticker
                )])
                fig_candle.update_layout(title=f"{selected_ticker} 캔들 차트", xaxis_rangeslider_visible=False)
                st.plotly_chart(fig_candle, use_container_width=True)

    except Exception as e:
        st.error(f"오류 발생: {e}")
else:
    st.info("왼쪽 사이드바에서 설정을 확인한 후 '데이터 불러오기' 버튼을 눌러주세요.")
