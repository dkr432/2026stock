import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

st.set_page_config(page_title="글로벌 주식 비교", layout="wide")

st.title("📈 글로벌 주식 비교 분석")
st.write("🇰🇷 한국 vs 🇺🇸 미국 주요 주식 수익률을 비교합니다.")

# 기간 선택
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input(
        "시작 날짜",
        datetime.date.today() - datetime.timedelta(days=180)
    )

with col2:
    end_date = st.date_input(
        "종료 날짜",
        datetime.date.today()
    )

# 주식 리스트
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

tickers = list(stocks.values())

# 데이터 다운로드
data = yf.download(
    tickers,
    start=start_date,
    end=end_date,
    auto_adjust=True,
    progress=False
)

# Close 데이터만 사용
close = data["Close"]

# 컬럼 이름 변경
close.columns = stocks.keys()

# 수익률 계산
returns = (close.iloc[-1] / close.iloc[0] - 1) * 100
returns = returns.sort_values(ascending=False)

st.subheader("📊 기간 수익률 비교")

returns_df = pd.DataFrame({
    "종목": returns.index,
    "수익률 (%)": returns.values.round(2)
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
    st.line_chart(close[selected])

# 개별 종목 분석
st.subheader("🔎 개별 종목 분석")

stock_choice = st.selectbox(
    "종목 선택",
    list(stocks.keys())
)

ticker = stocks[stock_choice]

hist = yf.download(
    ticker,
    start=start_date,
    end=end_date,
    auto_adjust=True,
    progress=False
)

if not hist.empty:

    st.line_chart(hist["Close"])

    close_series = hist["Close"]

    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]

    return_rate = (close_series.iloc[-1] / close_series.iloc[0] - 1) * 100

    st.metric(
        label=f"{stock_choice} 수익률",
        value=f"{return_rate:.2f}%"
    )

else:
    st.warning("주가 데이터를 불러오지 못했습니다.")

st.success("🚀 yfinance 기반 글로벌 주식 분석 앱")
