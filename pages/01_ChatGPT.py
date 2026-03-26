import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="📈 글로벌 주식 비교 분석", layout="wide")

st.title("📊 한국 🇰🇷 vs 미국 🇺🇸 주요 주식 수익률 비교")

st.write("기간을 선택하면 주요 기업의 수익률과 차트를 비교할 수 있습니다.")

# 기간 선택
start_date = st.date_input(
    "시작 날짜",
    datetime.date.today() - datetime.timedelta(days=180)
)

end_date = st.date_input(
    "종료 날짜",
    datetime.date.today()
)

# 주요 주식 리스트
stocks = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "네이버": "035420.KS",
    "카카오": "035720.KS",
    "애플": "AAPL",
    "마이크로소프트": "MSFT",
    "엔비디아": "NVDA",
    "아마존": "AMZN",
    "테슬라": "TSLA",
    "구글": "GOOGL"
}

# 데이터 가져오기
data = yf.download(list(stocks.values()), start=start_date, end=end_date)["Close"]

# 컬럼 이름 변경
data.columns = stocks.keys()

# 수익률 계산
returns = (data.iloc[-1] / data.iloc[0] - 1) * 100
returns = returns.sort_values(ascending=False)

# 수익률 테이블
st.subheader("📊 수익률 비교 (%)")

returns_df = pd.DataFrame({
    "Stock": returns.index,
    "Return (%)": returns.values
})

st.dataframe(returns_df, use_container_width=True)

# 차트
st.subheader("📈 주가 차트 비교")

selected = st.multiselect(
    "차트에 표시할 종목 선택",
    list(stocks.keys()),
    default=["삼성전자", "애플", "엔비디아"]
)

if selected:
    st.line_chart(data[selected])

# 개별 종목 보기
st.subheader("🔎 개별 종목 상세")

stock_choice = st.selectbox(
    "종목 선택",
    list(stocks.keys())
)

ticker = stocks[stock_choice]
hist = yf.download(ticker, start=start_date, end=end_date)

st.line_chart(hist["Close"])

st.metric(
    label=f"{stock_choice} 총 수익률",
    value=f"{((hist['Close'].iloc[-1]/hist['Close'].iloc[0]-1)*100):.2f}%"
)

st.success("🚀 yfinance 기반 글로벌 주식 비교 분석 앱")
