import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StockScope | 글로벌 주식 비교",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=Space+Mono:wght@400;700&family=Bebas+Neue&display=swap');

:root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2236;
    --border: #1e2d45;
    --accent: #00d4ff;
    --accent2: #ff6b6b;
    --green: #00e676;
    --red: #ff1744;
    --text: #e2e8f0;
    --muted: #64748b;
}

/* Global */
html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1525 50%, #0a0e1a 100%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}

/* Header */
.main-header {
    text-align: center;
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}

.main-title {
    font-family: 'Bebas Neue', cursive;
    font-size: 4rem;
    letter-spacing: 0.1em;
    background: linear-gradient(90deg, var(--accent), #7c3aed, var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1;
}

.main-subtitle {
    font-size: 0.9rem;
    color: var(--muted);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 0.5rem;
    font-family: 'Space Mono', monospace;
}

/* Metric Cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    transition: transform 0.2s, border-color 0.2s;
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), transparent);
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: var(--accent);
}

.metric-ticker {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: var(--accent);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}

.metric-name {
    font-size: 0.85rem;
    color: var(--muted);
    margin-bottom: 0.5rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.metric-price {
    font-family: 'Space Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text);
}

.metric-return {
    font-family: 'Space Mono', monospace;
    font-size: 0.95rem;
    font-weight: 700;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    display: inline-block;
    margin-top: 0.4rem;
}

.positive { color: var(--green); background: rgba(0,230,118,0.1); }
.negative { color: var(--red); background: rgba(255,23,68,0.1); }

/* Section Labels */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--muted);
    border-left: 3px solid var(--accent);
    padding-left: 0.8rem;
    margin: 1.5rem 0 1rem;
}

.kr-label { border-color: #ff6b6b; }
.us-label { border-color: #00d4ff; }

/* Chart container */
.chart-wrapper {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
}

/* Rank table */
.rank-row {
    display: flex;
    align-items: center;
    padding: 0.7rem 0;
    border-bottom: 1px solid var(--border);
}

.rank-num {
    font-family: 'Bebas Neue', cursive;
    font-size: 1.5rem;
    color: var(--border);
    width: 2rem;
    min-width: 2rem;
}

.rank-num.top { color: var(--accent); }

/* Streamlit overrides */
div[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
}

.stSelectbox > div > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

.stMultiSelect > div > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
}

div[data-testid="stTabs"] button {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.05em;
}

hr { border-color: var(--border); }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Stock Universe ───────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "현대차": "005380.KS",
    "POSCO홀딩스": "005490.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS",
    "기아": "000270.KS",
    "셀트리온": "068270.KS",
    "KB금융": "105560.KS",
    "신한지주": "055550.KS",
    "LG화학": "051910.KS",
    "삼성바이오로직스": "207940.KS",
    "현대모비스": "012330.KS",
    "SK이노베이션": "096770.KS",
}

US_STOCKS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Alphabet": "GOOGL",
    "Amazon": "AMZN",
    "Meta": "META",
    "Tesla": "TSLA",
    "Broadcom": "AVGO",
    "Taiwan Semi (ADR)": "TSM",
    "Berkshire": "BRK-B",
    "JPMorgan": "JPM",
    "Eli Lilly": "LLY",
    "Visa": "V",
    "Netflix": "NFLX",
    "AMD": "AMD",
}

INDICES = {
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",
}

PERIOD_MAP = {
    "1주": "5d",
    "1개월": "1mo",
    "3개월": "3mo",
    "6개월": "6mo",
    "1년": "1y",
    "2년": "2y",
    "5년": "5y",
}

# ── Helper Functions ─────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_stock_data(tickers: list, period: str):
    """Fetch OHLCV data for multiple tickers."""
    data = {}
    for ticker in tickers:
        try:
            tk = yf.Ticker(ticker)
            hist = tk.history(period=period)
            if not hist.empty:
                data[ticker] = hist
        except Exception:
            pass
    return data


@st.cache_data(ttl=300)
def fetch_current_info(tickers: list):
    """Fetch current price and basic info."""
    results = {}
    for ticker in tickers:
        try:
            tk = yf.Ticker(ticker)
            info = tk.fast_info
            results[ticker] = {
                "price": getattr(info, "last_price", None),
                "currency": getattr(info, "currency", ""),
                "52w_high": getattr(info, "year_high", None),
                "52w_low": getattr(info, "year_low", None),
                "market_cap": getattr(info, "market_cap", None),
            }
        except Exception:
            results[ticker] = {}
    return results


def calc_returns(hist_dict: dict):
    """Calculate cumulative returns (normalised to 100 at start)."""
    returns = {}
    for ticker, hist in hist_dict.items():
        if hist is not None and not hist.empty and len(hist) > 1:
            close = hist["Close"].dropna()
            returns[ticker] = (close / close.iloc[0]) * 100
    return returns


def format_price(price, currency=""):
    if price is None:
        return "N/A"
    if currency == "KRW":
        return f"₩{price:,.0f}"
    return f"${price:,.2f}"


def format_pct(val):
    if val is None:
        return "N/A"
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.2f}%"


def get_period_return(hist):
    if hist is None or hist.empty or len(hist) < 2:
        return None
    close = hist["Close"].dropna()
    if len(close) < 2:
        return None
    return (close.iloc[-1] / close.iloc[0] - 1) * 100


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    st.markdown("---")

    period_label = st.selectbox(
        "📅 조회 기간",
        list(PERIOD_MAP.keys()),
        index=3,
    )
    period = PERIOD_MAP[period_label]

    st.markdown("---")
    st.markdown("**🇰🇷 한국 종목**")
    kr_selected = st.multiselect(
        "한국 종목 선택",
        list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "NAVER", "현대차", "카카오"],
        label_visibility="collapsed",
    )

    st.markdown("**🇺🇸 미국 종목**")
    us_selected = st.multiselect(
        "미국 종목 선택",
        list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Microsoft", "Tesla", "Meta"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    show_indices = st.checkbox("📊 주요 지수 포함", value=True)
    show_volume = st.checkbox("📦 거래량 표시", value=False)
    chart_type = st.radio("차트 유형", ["수익률 비교", "캔들스틱"], horizontal=True)

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.75rem; color:#64748b; font-family:Space Mono,monospace;'>"
        "⏱ 데이터: yfinance<br>🔄 5분 캐시"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1 class="main-title">StockScope</h1>
  <p class="main-subtitle">한국 · 미국 글로벌 주식 비교 대시보드</p>
</div>
""", unsafe_allow_html=True)

# ── Validate Selection ───────────────────────────────────────────────────────
if not kr_selected and not us_selected:
    st.warning("👈 사이드바에서 종목을 하나 이상 선택해주세요.")
    st.stop()

kr_tickers = {name: KR_STOCKS[name] for name in kr_selected}
us_tickers = {name: US_STOCKS[name] for name in us_selected}
all_named = {**kr_tickers, **us_tickers}
all_tickers = list(all_named.values())

index_tickers = list(INDICES.values()) if show_indices else []

# ── Fetch Data ───────────────────────────────────────────────────────────────
with st.spinner("📡 시장 데이터 수신 중..."):
    stock_data = fetch_stock_data(all_tickers + index_tickers, period)
    info_data = fetch_current_info(all_tickers)

# reverse map ticker → name
ticker_to_name = {v: k for k, v in all_named.items()}
ticker_to_name.update({v: k for k, v in INDICES.items()})

# ── INDEX STRIP ──────────────────────────────────────────────────────────────
if show_indices:
    st.markdown('<p class="section-label">📊 주요 지수</p>', unsafe_allow_html=True)
    idx_cols = st.columns(len(INDICES))
    for col, (idx_name, idx_ticker) in zip(idx_cols, INDICES.items()):
        hist = stock_data.get(idx_ticker)
        ret = get_period_return(hist)
        cls = "positive" if ret and ret >= 0 else "negative"
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-ticker">{idx_ticker}</div>
              <div class="metric-name">{idx_name}</div>
              <div class="metric-price" style="font-size:1rem">
                {"N/A" if hist is None or hist.empty else f"{hist['Close'].iloc[-1]:,.2f}"}
              </div>
              <span class="metric-return {cls}">{format_pct(ret)}</span>
            </div>
            """, unsafe_allow_html=True)

# ── STOCK CARDS ──────────────────────────────────────────────────────────────
if kr_selected:
    st.markdown('<p class="section-label kr-label">🇰🇷 한국 종목</p>', unsafe_allow_html=True)
    kr_cols = st.columns(min(len(kr_selected), 5))
    for col, name in zip(kr_cols, kr_selected):
        ticker = KR_STOCKS[name]
        hist = stock_data.get(ticker)
        info = info_data.get(ticker, {})
        ret = get_period_return(hist)
        price = info.get("price")
        currency = info.get("currency", "KRW")
        cls = "positive" if ret and ret >= 0 else "negative"
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-ticker">{ticker.replace('.KS','')}</div>
              <div class="metric-name">{name}</div>
              <div class="metric-price">{format_price(price, currency)}</div>
              <span class="metric-return {cls}">{format_pct(ret)}</span>
            </div>
            """, unsafe_allow_html=True)

if us_selected:
    st.markdown('<p class="section-label us-label">🇺🇸 미국 종목</p>', unsafe_allow_html=True)
    us_cols = st.columns(min(len(us_selected), 5))
    for col, name in zip(us_cols, us_selected):
        ticker = US_STOCKS[name]
        hist = stock_data.get(ticker)
        info = info_data.get(ticker, {})
        ret = get_period_return(hist)
        price = info.get("price")
        currency = info.get("currency", "USD")
        cls = "positive" if ret and ret >= 0 else "negative"
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-ticker">{ticker}</div>
              <div class="metric-name">{name}</div>
              <div class="metric-price">{format_price(price, currency)}</div>
              <span class="metric-return {cls}">{format_pct(ret)}</span>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── MAIN CHART ───────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 수익률 비교", "🕯 캔들스틱", "🏆 수익률 랭킹"])

# Colour palette
COLORS_KR = ["#ff6b6b", "#ff9f43", "#ffd32a", "#ff4757", "#ff6348"]
COLORS_US = ["#00d4ff", "#7c3aed", "#06b6d4", "#818cf8", "#38bdf8"]
COLORS_IDX = ["#a3e635", "#34d399", "#f59e0b", "#f472b6", "#94a3b8"]

with tab1:
    fig = go.Figure()

    # Indices (dashed)
    if show_indices:
        for i, (idx_name, idx_ticker) in enumerate(INDICES.items()):
            hist = stock_data.get(idx_ticker)
            if hist is not None and not hist.empty:
                close = hist["Close"].dropna()
                norm = (close / close.iloc[0]) * 100
                fig.add_trace(go.Scatter(
                    x=norm.index, y=norm.values,
                    name=idx_name,
                    line=dict(color=COLORS_IDX[i % len(COLORS_IDX)], width=1.5, dash="dot"),
                    opacity=0.7,
                    hovertemplate=f"<b>{idx_name}</b><br>%{{x|%Y-%m-%d}}<br>수익률: %{{y:.2f}}<extra></extra>",
                ))

    # KR Stocks
    for i, name in enumerate(kr_selected):
        ticker = KR_STOCKS[name]
        hist = stock_data.get(ticker)
        if hist is not None and not hist.empty:
            close = hist["Close"].dropna()
            norm = (close / close.iloc[0]) * 100
            fig.add_trace(go.Scatter(
                x=norm.index, y=norm.values,
                name=f"🇰🇷 {name}",
                line=dict(color=COLORS_KR[i % len(COLORS_KR)], width=2.5),
                hovertemplate=f"<b>🇰🇷 {name}</b><br>%{{x|%Y-%m-%d}}<br>기준=100 → %{{y:.2f}}<extra></extra>",
            ))

    # US Stocks
    for i, name in enumerate(us_selected):
        ticker = US_STOCKS[name]
        hist = stock_data.get(ticker)
        if hist is not None and not hist.empty:
            close = hist["Close"].dropna()
            norm = (close / close.iloc[0]) * 100
            fig.add_trace(go.Scatter(
                x=norm.index, y=norm.values,
                name=f"🇺🇸 {name}",
                line=dict(color=COLORS_US[i % len(COLORS_US)], width=2.5),
                hovertemplate=f"<b>🇺🇸 {name}</b><br>%{{x|%Y-%m-%d}}<br>기준=100 → %{{y:.2f}}<extra></extra>",
            ))

    # Baseline
    fig.add_hline(y=100, line_dash="dash", line_color="#334155", line_width=1)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.6)",
        font=dict(family="Noto Sans KR", color="#e2e8f0"),
        legend=dict(
            bgcolor="rgba(17,24,39,0.8)",
            bordercolor="#1e2d45",
            borderwidth=1,
            font=dict(size=11),
        ),
        hovermode="x unified",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=True,
            linecolor="#1e2d45",
            tickfont=dict(size=11, color="#64748b"),
        ),
        yaxis=dict(
            title="수익률 지수 (시작=100)",
            showgrid=True,
            gridcolor="#1e2d45",
            zeroline=False,
            tickfont=dict(size=11, color="#64748b"),
            ticksuffix="",
        ),
        height=500,
        margin=dict(l=10, r=10, t=20, b=10),
        hoverlabel=dict(
            bgcolor="#111827",
            bordercolor="#1e2d45",
            font=dict(family="Space Mono", size=12),
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Volume chart
    if show_volume and all_tickers:
        st.markdown('<p class="section-label">📦 거래량</p>', unsafe_allow_html=True)
        all_names_list = kr_selected + us_selected
        all_col_list = COLORS_KR[:len(kr_selected)] + COLORS_US[:len(us_selected)]
        vol_tickers = [KR_STOCKS.get(n) or US_STOCKS.get(n) for n in all_names_list]

        subfig = make_subplots(
            rows=1, cols=len(vol_tickers),
            subplot_titles=[f"{'🇰🇷' if n in kr_selected else '🇺🇸'} {n}" for n in all_names_list],
        )
        for idx, (name, ticker, color) in enumerate(zip(all_names_list, vol_tickers, all_col_list)):
            hist = stock_data.get(ticker)
            if hist is not None and not hist.empty:
                subfig.add_trace(
                    go.Bar(x=hist.index, y=hist["Volume"], name=name,
                           marker_color=color, opacity=0.7, showlegend=False),
                    row=1, col=idx + 1,
                )
        subfig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17,24,39,0.6)",
            font=dict(color="#e2e8f0"),
            height=200,
            margin=dict(l=5, r=5, t=30, b=5),
        )
        subfig.update_xaxes(showgrid=False, linecolor="#1e2d45")
        subfig.update_yaxes(showgrid=True, gridcolor="#1e2d45")
        st.plotly_chart(subfig, use_container_width=True)

with tab2:
    # Candle chart: pick one stock
    candle_options = {f"🇰🇷 {n}": KR_STOCKS[n] for n in kr_selected}
    candle_options.update({f"🇺🇸 {n}": US_STOCKS[n] for n in us_selected})

    if not candle_options:
        st.info("종목을 선택해주세요.")
    else:
        chosen = st.selectbox("종목 선택", list(candle_options.keys()))
        chosen_ticker = candle_options[chosen]
        hist = stock_data.get(chosen_ticker)

        if hist is None or hist.empty:
            st.warning("데이터를 불러올 수 없습니다.")
        else:
            candle_fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                row_heights=[0.75, 0.25],
                vertical_spacing=0.03,
            )

            # Candles
            candle_fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist["Open"], high=hist["High"],
                low=hist["Low"], close=hist["Close"],
                name=chosen,
                increasing_line_color="#00e676",
                decreasing_line_color="#ff1744",
                increasing_fillcolor="#00e676",
                decreasing_fillcolor="#ff1744",
            ), row=1, col=1)

            # MA 20
            if len(hist) >= 20:
                ma20 = hist["Close"].rolling(20).mean()
                candle_fig.add_trace(go.Scatter(
                    x=hist.index, y=ma20,
                    name="MA20", line=dict(color="#ffd32a", width=1.5),
                ), row=1, col=1)

            # MA 60
            if len(hist) >= 60:
                ma60 = hist["Close"].rolling(60).mean()
                candle_fig.add_trace(go.Scatter(
                    x=hist.index, y=ma60,
                    name="MA60", line=dict(color="#00d4ff", width=1.5),
                ), row=1, col=1)

            # Volume
            colors_vol = ["#00e676" if c >= o else "#ff1744"
                          for c, o in zip(hist["Close"], hist["Open"])]
            candle_fig.add_trace(go.Bar(
                x=hist.index, y=hist["Volume"],
                name="거래량",
                marker_color=colors_vol,
                opacity=0.6,
                showlegend=False,
            ), row=2, col=1)

            candle_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(17,24,39,0.6)",
                font=dict(family="Noto Sans KR", color="#e2e8f0"),
                xaxis_rangeslider_visible=False,
                height=550,
                legend=dict(bgcolor="rgba(17,24,39,0.8)", bordercolor="#1e2d45", borderwidth=1),
                margin=dict(l=10, r=10, t=20, b=10),
                hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2d45", font=dict(family="Space Mono")),
            )
            candle_fig.update_xaxes(showgrid=False, linecolor="#1e2d45")
            candle_fig.update_yaxes(showgrid=True, gridcolor="#1e2d45")

            st.plotly_chart(candle_fig, use_container_width=True)

with tab3:
    # Ranking table
    rank_data = []
    for name in kr_selected:
        ticker = KR_STOCKS[name]
        hist = stock_data.get(ticker)
        ret = get_period_return(hist)
        info = info_data.get(ticker, {})
        price = info.get("price")
        mc = info.get("market_cap")
        rank_data.append({
            "국가": "🇰🇷",
            "종목": name,
            "티커": ticker.replace(".KS", ""),
            "현재가": format_price(price, "KRW"),
            "수익률": ret,
            "시가총액": f"₩{mc/1e12:.1f}조" if mc else "N/A",
        })
    for name in us_selected:
        ticker = US_STOCKS[name]
        hist = stock_data.get(ticker)
        ret = get_period_return(hist)
        info = info_data.get(ticker, {})
        price = info.get("price")
        mc = info.get("market_cap")
        rank_data.append({
            "국가": "🇺🇸",
            "종목": name,
            "티커": ticker,
            "현재가": format_price(price, "USD"),
            "수익률": ret,
            "시가총액": f"${mc/1e9:.0f}B" if mc else "N/A",
        })

    rank_data.sort(key=lambda x: (x["수익률"] or -999), reverse=True)

    # Bar chart
    names_r = [f"{d['국가']} {d['종목']}" for d in rank_data]
    rets_r = [d["수익률"] or 0 for d in rank_data]
    colors_r = ["#00e676" if r >= 0 else "#ff1744" for r in rets_r]

    bar_fig = go.Figure(go.Bar(
        y=names_r[::-1], x=rets_r[::-1],
        orientation="h",
        marker_color=colors_r[::-1],
        text=[format_pct(r) for r in rets_r[::-1]],
        textposition="outside",
        textfont=dict(family="Space Mono", size=11, color="#e2e8f0"),
        hovertemplate="<b>%{y}</b><br>수익률: %{x:.2f}%<extra></extra>",
    ))
    bar_fig.add_vline(x=0, line_color="#334155", line_width=1)
    bar_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.6)",
        font=dict(family="Noto Sans KR", color="#e2e8f0"),
        xaxis=dict(
            title=f"수익률 ({period_label})",
            showgrid=True, gridcolor="#1e2d45",
            ticksuffix="%",
            tickfont=dict(size=11, color="#64748b"),
        ),
        yaxis=dict(showgrid=False, tickfont=dict(size=12)),
        height=max(350, len(rank_data) * 48),
        margin=dict(l=10, r=80, t=20, b=10),
        hoverlabel=dict(bgcolor="#111827", bordercolor="#1e2d45"),
    )
    st.plotly_chart(bar_fig, use_container_width=True)

    # Table
    st.markdown('<p class="section-label">📋 상세 데이터</p>', unsafe_allow_html=True)
    df = pd.DataFrame(rank_data)
    df["수익률_표시"] = df["수익률"].apply(format_pct)
    df_show = df[["국가", "종목", "티커", "현재가", "수익률_표시", "시가총액"]].rename(
        columns={"수익률_표시": f"수익률 ({period_label})"}
    )
    st.dataframe(
        df_show,
        use_container_width=True,
        hide_index=True,
    )

# ── Correlation Heatmap ──────────────────────────────────────────────────────
if len(all_tickers) >= 2:
    st.markdown("---")
    st.markdown('<p class="section-label">🔗 수익률 상관관계 히트맵</p>', unsafe_allow_html=True)

    returns_series = {}
    for name, ticker in all_named.items():
        hist = stock_data.get(ticker)
        if hist is not None and not hist.empty and len(hist) > 5:
            returns_series[f"{'🇰🇷' if ticker in kr_tickers.values() else '🇺🇸'} {name}"] = \
                hist["Close"].pct_change().dropna()

    if len(returns_series) >= 2:
        df_ret = pd.DataFrame(returns_series).dropna()
        corr = df_ret.corr()

        heat_fig = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale=[
                [0.0, "#ff1744"], [0.5, "#111827"], [1.0, "#00d4ff"]
            ],
            zmid=0,
            text=[[f"{v:.2f}" for v in row] for row in corr.values],
            texttemplate="%{text}",
            textfont=dict(family="Space Mono", size=11),
            hovertemplate="%{y} × %{x}<br>상관계수: %{z:.3f}<extra></extra>",
        ))
        heat_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17,24,39,0.6)",
            font=dict(family="Noto Sans KR", color="#e2e8f0"),
            height=max(350, len(returns_series) * 55),
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(tickangle=-30, tickfont=dict(size=10)),
            yaxis=dict(tickfont=dict(size=10)),
        )
        st.plotly_chart(heat_fig, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#334155; font-family:Space Mono,monospace; font-size:0.72rem; padding:1rem 0'>"
    "StockScope · Powered by yfinance & Streamlit · 투자 정보 참고용이며 투자 권유가 아닙니다"
    "</div>",
    unsafe_allow_html=True,
)
