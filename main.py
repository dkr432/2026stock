import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StockScope",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=JetBrains+Mono:wght@400;600;700&family=Anton&display=swap');

:root {
    --bg0:       #050810;
    --bg1:       #080d18;
    --bg2:       #0c1220;
    --bg3:       #111928;
    --border:    rgba(255,255,255,0.07);
    --border2:   rgba(255,255,255,0.12);
    --text:      #f0f4ff;
    --muted:     #4a5a78;
    --muted2:    #6b7fa3;
    --kr:        #ff4d6d;
    --kr-glow:   rgba(255,77,109,0.35);
    --kr-soft:   rgba(255,77,109,0.12);
    --us:        #00c6ff;
    --us-glow:   rgba(0,198,255,0.35);
    --us-soft:   rgba(0,198,255,0.10);
    --green:     #0dff8c;
    --green-bg:  rgba(13,255,140,0.10);
    --red:       #ff3355;
    --red-bg:    rgba(255,51,85,0.10);
    --gold:      #ffd166;
    --purple:    #a78bfa;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif !important;
    color: var(--text) !important;
}
.stApp {
    background: radial-gradient(ellipse 120% 60% at 50% 0%, #0a1628 0%, var(--bg0) 60%) !important;
}
section[data-testid="stSidebar"] {
    background: var(--bg1) !important;
    border-right: 1px solid var(--border2) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}
.stMultiSelect span[data-baseweb="tag"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
}

/* HEADER */
.hdr-wrap {
    display: flex; flex-direction: column;
    align-items: center; padding: 2.5rem 0 2rem;
    position: relative;
}
.hdr-glow {
    position: absolute; top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 200px;
    background: radial-gradient(ellipse, rgba(0,198,255,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hdr-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; letter-spacing: 0.35em;
    color: var(--us); text-transform: uppercase;
    margin-bottom: 0.5rem; opacity: 0.8;
}
.hdr-title {
    font-family: 'Anton', sans-serif;
    font-size: clamp(3.5rem, 8vw, 6rem);
    letter-spacing: 0.04em; line-height: 1; margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, var(--us) 40%, var(--purple) 70%, var(--kr) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    filter: drop-shadow(0 0 40px rgba(0,198,255,0.25));
}
.hdr-sub {
    font-size: 0.8rem; color: var(--muted2);
    letter-spacing: 0.15em; margin-top: 0.6rem; font-weight: 300;
}
.hdr-divider {
    width: 100%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--border2) 20%, var(--us) 50%, var(--border2) 80%, transparent);
    margin-top: 1.5rem; opacity: 0.5;
}

/* SECTION LABEL */
.sec-label {
    display: flex; align-items: center; gap: 0.6rem; margin: 1.6rem 0 0.9rem;
}
.sec-line { flex: 1; height: 1px; background: var(--border); }
.sec-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; letter-spacing: 0.25em; text-transform: uppercase;
    padding: 0.25rem 0.8rem; border-radius: 4px; white-space: nowrap;
}
.sec-text.idx { color: var(--gold);   border: 1px solid rgba(255,209,102,0.25); background: rgba(255,209,102,0.06); }
.sec-text.kr  { color: var(--kr);     border: 1px solid rgba(255,77,109,0.3);   background: var(--kr-soft); }
.sec-text.us  { color: var(--us);     border: 1px solid rgba(0,198,255,0.25);   background: var(--us-soft); }

/* BADGE */
.badge {
    display: inline-flex; align-items: center; gap: 0.25rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem; font-weight: 700;
    padding: 0.3rem 0.7rem; border-radius: 6px; letter-spacing: 0.02em;
}
.badge.up   { color: var(--green); background: var(--green-bg); border: 1px solid rgba(13,255,140,0.3); }
.badge.down { color: var(--red);   background: var(--red-bg);   border: 1px solid rgba(255,51,85,0.3); }
.badge.flat { color: var(--muted2); background: var(--bg3);     border: 1px solid var(--border2); }

/* INDEX CARD */
.idx-card {
    background: linear-gradient(145deg, #0e1828 0%, #0a1220 100%);
    border: 1px solid rgba(255,209,102,0.18);
    border-radius: 14px; padding: 1.1rem 1.3rem 1rem;
    position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.idx-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 2px; background: linear-gradient(90deg, var(--gold), transparent);
}
.idx-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.6), 0 0 24px rgba(255,209,102,0.12);
}
.idx-ticker { font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:var(--gold); letter-spacing:0.1em; margin-bottom:0.2rem; opacity:0.85; }
.idx-name   { font-size:0.78rem; color:var(--muted2); margin-bottom:0.55rem; font-weight:300; }
.idx-price  { font-family:'JetBrains Mono',monospace; font-size:1.25rem; font-weight:700; color:#ffffff; margin-bottom:0.5rem; }

/* KR STOCK CARD */
.kr-card {
    background: linear-gradient(150deg, #110d14 0%, #0c0f18 100%);
    border: 1px solid rgba(255,77,109,0.22);
    border-radius: 14px; padding: 1.1rem 1.25rem 1rem;
    position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
    height: 100%;
}
.kr-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 2px; background: linear-gradient(90deg, var(--kr), transparent);
}
.kr-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.7), 0 0 30px var(--kr-glow);
    border-color: rgba(255,77,109,0.5);
}

/* US STOCK CARD */
.us-card {
    background: linear-gradient(150deg, #091218 0%, #080d18 100%);
    border: 1px solid rgba(0,198,255,0.2);
    border-radius: 14px; padding: 1.1rem 1.25rem 1rem;
    position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
    height: 100%;
}
.us-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 2px; background: linear-gradient(90deg, var(--us), transparent);
}
.us-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.7), 0 0 30px var(--us-glow);
    border-color: rgba(0,198,255,0.45);
}

.flag-line  { font-family:'JetBrains Mono',monospace; font-size:0.65rem; letter-spacing:0.12em; margin-bottom:0.2rem; opacity:0.85; }
.flag-kr    { color: var(--kr); }
.flag-us    { color: var(--us); }
.stock-name { font-size:0.9rem; font-weight:700; color:var(--text); margin-bottom:0.5rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.stock-price{ font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:600; color:#fff; margin-bottom:0.5rem; }
.stock-mc   { margin-top:0.45rem; font-size:0.68rem; color:var(--muted); font-family:'JetBrains Mono',monospace; }

/* TABS */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--bg2) !important; border-radius: 10px !important;
    padding: 4px !important; gap: 2px !important; border: 1px solid var(--border) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important; letter-spacing: 0.05em !important;
    border-radius: 7px !important; padding: 0.5rem 1.2rem !important;
    color: var(--muted2) !important; border: none !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--bg3) !important; color: var(--text) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4) !important;
}

hr { border-color: var(--border) !important; }
div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
.stCheckbox label, .stRadio label { color: var(--text) !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg0); }
::-webkit-scrollbar-thumb { background: var(--bg3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자":"005930.KS","SK하이닉스":"000660.KS","LG에너지솔루션":"373220.KS",
    "현대차":"005380.KS","POSCO홀딩스":"005490.KS","NAVER":"035420.KS",
    "카카오":"035720.KS","기아":"000270.KS","셀트리온":"068270.KS",
    "KB금융":"105560.KS","신한지주":"055550.KS","LG화학":"051910.KS",
    "삼성바이오":"207940.KS","현대모비스":"012330.KS","SK이노베이션":"096770.KS",
}
US_STOCKS = {
    "Apple":"AAPL","Microsoft":"MSFT","NVIDIA":"NVDA","Alphabet":"GOOGL",
    "Amazon":"AMZN","Meta":"META","Tesla":"TSLA","Broadcom":"AVGO",
    "TSMC (ADR)":"TSM","Berkshire":"BRK-B","JPMorgan":"JPM","Eli Lilly":"LLY",
    "Visa":"V","Netflix":"NFLX","AMD":"AMD",
}
INDICES = {"KOSPI":"^KS11","KOSDAQ":"^KQ11","S&P 500":"^GSPC","NASDAQ":"^IXIC","Dow Jones":"^DJI"}
PERIOD_MAP = {"1주":"5d","1개월":"1mo","3개월":"3mo","6개월":"6mo","1년":"1y","2년":"2y","5년":"5y"}

@st.cache_data(ttl=300)
def fetch_hist(tickers, period):
    out = {}
    for t in tickers:
        try:
            h = yf.Ticker(t).history(period=period)
            if not h.empty: out[t] = h
        except: pass
    return out

@st.cache_data(ttl=300)
def fetch_info(tickers):
    out = {}
    for t in tickers:
        try:
            fi = yf.Ticker(t).fast_info
            out[t] = {"price":getattr(fi,"last_price",None),
                      "currency":getattr(fi,"currency",""),
                      "market_cap":getattr(fi,"market_cap",None)}
        except: out[t] = {}
    return out

def period_return(h):
    if h is None or h.empty or len(h) < 2: return None
    c = h["Close"].dropna()
    return (c.iloc[-1]/c.iloc[0]-1)*100 if len(c)>=2 else None

def fmt_price(p, cur=""):
    if p is None: return "—"
    return f"₩{p:,.0f}" if cur=="KRW" else f"${p:,.2f}"

def fmt_pct(v):
    if v is None: return "—"
    return f"+{v:.2f}%" if v>=0 else f"{v:.2f}%"

def badge(v):
    if v is None: return '<span class="badge flat">—</span>'
    cls = "up" if v>=0 else "down"
    arrow = "▲" if v>=0 else "▼"
    return f'<span class="badge {cls}">{arrow} {fmt_pct(v)}</span>'

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ StockScope")
    st.markdown("---")
    period_label = st.selectbox("📅 조회 기간", list(PERIOD_MAP.keys()), index=3)
    period = PERIOD_MAP[period_label]
    st.markdown("---")
    st.markdown("**🇰🇷 한국 종목**")
    kr_sel = st.multiselect("KR", list(KR_STOCKS.keys()),
        default=["삼성전자","SK하이닉스","NAVER","현대차","카카오"],
        label_visibility="collapsed")
    st.markdown("**🇺🇸 미국 종목**")
    us_sel = st.multiselect("US", list(US_STOCKS.keys()),
        default=["Apple","NVIDIA","Microsoft","Tesla","Meta"],
        label_visibility="collapsed")
    st.markdown("---")
    show_idx = st.checkbox("주요 지수 포함", value=True)
    show_vol = st.checkbox("거래량 표시",    value=False)
    st.markdown("---")
    st.markdown("<div style='font-size:.7rem;color:#4a5a78;font-family:JetBrains Mono,monospace'>data · yfinance<br>cache · 5 min</div>", unsafe_allow_html=True)

if not kr_sel and not us_sel:
    st.warning("👈 사이드바에서 종목을 선택해주세요.")
    st.stop()

kr_map = {n:KR_STOCKS[n] for n in kr_sel}
us_map = {n:US_STOCKS[n] for n in us_sel}
all_map = {**kr_map, **us_map}
all_t = list(all_map.values())
idx_t = list(INDICES.values()) if show_idx else []

with st.spinner("⚡ 데이터 수신 중..."):
    hist_data = fetch_hist(all_t + idx_t, period)
    info_data = fetch_info(all_t)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hdr-wrap">
  <div class="hdr-glow"></div>
  <div class="hdr-eyebrow">GLOBAL EQUITY DASHBOARD</div>
  <h1 class="hdr-title">StockScope</h1>
  <p class="hdr-sub">한국 · 미국 글로벌 주식 실시간 비교</p>
  <div class="hdr-divider"></div>
</div>""", unsafe_allow_html=True)

# ── Index Row ─────────────────────────────────────────────────────────────────
if show_idx:
    st.markdown('<div class="sec-label"><div class="sec-line"></div><span class="sec-text idx">📊 MAJOR INDICES</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
    cols = st.columns(len(INDICES))
    for col,(name,ticker) in zip(cols, INDICES.items()):
        h = hist_data.get(ticker)
        ret = period_return(h)
        price_str = f"{h['Close'].iloc[-1]:,.2f}" if h is not None and not h.empty else "—"
        with col:
            st.markdown(f"""
            <div class="idx-card">
              <div class="idx-ticker">{ticker}</div>
              <div class="idx-name">{name}</div>
              <div class="idx-price">{price_str}</div>
              {badge(ret)}
            </div>""", unsafe_allow_html=True)

# ── KR Cards ──────────────────────────────────────────────────────────────────
if kr_sel:
    st.markdown('<div class="sec-label"><div class="sec-line"></div><span class="sec-text kr">🇰🇷 KOREA</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
    n_cols = min(len(kr_sel), 5)
    cols = st.columns(n_cols)
    for i, name in enumerate(kr_sel):
        ticker = KR_STOCKS[name]
        h   = hist_data.get(ticker)
        inf = info_data.get(ticker, {})
        ret = period_return(h)
        price = fmt_price(inf.get("price"), inf.get("currency","KRW"))
        mc  = inf.get("market_cap")
        mc_str = f"₩{mc/1e12:.1f}조" if mc else ""
        with cols[i % n_cols]:
            st.markdown(f"""
            <div class="kr-card">
              <div class="flag-line flag-kr">KRX · {ticker.replace('.KS','')}</div>
              <div class="stock-name">{name}</div>
              <div class="stock-price">{price}</div>
              {badge(ret)}
              {"<div class='stock-mc'>시총 "+mc_str+"</div>" if mc_str else ""}
            </div>""", unsafe_allow_html=True)

# ── US Cards ──────────────────────────────────────────────────────────────────
if us_sel:
    st.markdown('<div class="sec-label"><div class="sec-line"></div><span class="sec-text us">🇺🇸 USA</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
    n_cols = min(len(us_sel), 5)
    cols = st.columns(n_cols)
    for i, name in enumerate(us_sel):
        ticker = US_STOCKS[name]
        h   = hist_data.get(ticker)
        inf = info_data.get(ticker, {})
        ret = period_return(h)
        price = fmt_price(inf.get("price"), inf.get("currency","USD"))
        mc  = inf.get("market_cap")
        mc_str = f"${mc/1e9:.0f}B" if mc else ""
        with cols[i % n_cols]:
            st.markdown(f"""
            <div class="us-card">
              <div class="flag-line flag-us">NYSE/NQ · {ticker}</div>
              <div class="stock-name">{name}</div>
              <div class="stock-price">{price}</div>
              {badge(ret)}
              {"<div class='stock-mc'>mktcap "+mc_str+"</div>" if mc_str else ""}
            </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Chart Tabs ────────────────────────────────────────────────────────────────
KR_C = ["#ff4d6d","#ff6b6b","#ff8fa3","#ffb3c1","#ff0044"]
US_C = ["#00c6ff","#6ee7f7","#38bdf8","#818cf8","#a78bfa"]
IX_C = ["#ffd166","#ffc233","#e5a010","#f59e0b","#ca8a04"]

tab1, tab2, tab3 = st.tabs(["  📈 수익률 비교  ", "  🕯 캔들스틱  ", "  🏆 수익률 랭킹  "])

with tab1:
    fig = go.Figure()
    if show_idx:
        for i,(iname,itick) in enumerate(INDICES.items()):
            h = hist_data.get(itick)
            if h is not None and len(h)>1:
                c = h["Close"].dropna()
                fig.add_trace(go.Scatter(x=c.index, y=(c/c.iloc[0])*100,
                    name=iname, line=dict(color=IX_C[i%5], width=1.2, dash="dot"), opacity=0.6,
                    hovertemplate=f"<b>{iname}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.2f}}<extra></extra>"))
    for i,name in enumerate(kr_sel):
        h = hist_data.get(KR_STOCKS[name])
        if h is not None and len(h)>1:
            c = h["Close"].dropna()
            fig.add_trace(go.Scatter(x=c.index, y=(c/c.iloc[0])*100,
                name=f"🇰🇷 {name}", line=dict(color=KR_C[i%5], width=2.5),
                hovertemplate=f"<b>🇰🇷 {name}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.2f}}<extra></extra>"))
    for i,name in enumerate(us_sel):
        h = hist_data.get(US_STOCKS[name])
        if h is not None and len(h)>1:
            c = h["Close"].dropna()
            fig.add_trace(go.Scatter(x=c.index, y=(c/c.iloc[0])*100,
                name=f"🇺🇸 {name}", line=dict(color=US_C[i%5], width=2.5),
                hovertemplate=f"<b>🇺🇸 {name}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.2f}}<extra></extra>"))
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.08)", line_width=1)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(8,13,24,0.85)",
        font=dict(family="JetBrains Mono", color="#6b7fa3", size=11),
        height=520, margin=dict(l=0,r=0,t=16,b=0), hovermode="x unified",
        hoverlabel=dict(bgcolor="#0c1220", bordercolor="rgba(255,255,255,0.1)",
            font=dict(family="JetBrains Mono", size=12, color="#f0f4ff")),
        legend=dict(bgcolor="rgba(8,13,24,0.9)", bordercolor="rgba(255,255,255,0.08)",
            borderwidth=1, font=dict(size=11, color="#f0f4ff")),
        xaxis=dict(showgrid=False, zeroline=False, linecolor="rgba(255,255,255,0.06)",
            tickfont=dict(size=10)),
        yaxis=dict(title="수익률 지수 (시작=100)", titlefont=dict(size=10, color="#4a5a78"),
            showgrid=True, gridcolor="rgba(255,255,255,0.04)", zeroline=False,
            tickfont=dict(size=10)),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

    if show_vol:
        all_nv = kr_sel + us_sel
        all_tv = [KR_STOCKS.get(n) or US_STOCKS.get(n) for n in all_nv]
        all_cv = KR_C[:len(kr_sel)] + US_C[:len(us_sel)]
        if all_nv:
            vfig = make_subplots(rows=1, cols=len(all_nv),
                subplot_titles=[f"{'🇰🇷' if n in kr_sel else '🇺🇸'} {n}" for n in all_nv])
            for j,(nm,tk,cl) in enumerate(zip(all_nv,all_tv,all_cv)):
                h = hist_data.get(tk)
                if h is not None and not h.empty:
                    vfig.add_trace(go.Bar(x=h.index, y=h["Volume"], name=nm,
                        marker_color=cl, opacity=0.75, showlegend=False), row=1, col=j+1)
            vfig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(8,13,24,0.85)",
                font=dict(color="#6b7fa3", size=10), height=180, margin=dict(l=0,r=0,t=28,b=0))
            vfig.update_xaxes(showgrid=False, linecolor="rgba(255,255,255,0.05)")
            vfig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)")
            st.plotly_chart(vfig, use_container_width=True, config={"displayModeBar":False})

with tab2:
    opts = {f"🇰🇷 {n}": KR_STOCKS[n] for n in kr_sel}
    opts.update({f"🇺🇸 {n}": US_STOCKS[n] for n in us_sel})
    if not opts:
        st.info("종목을 선택해주세요.")
    else:
        chosen = st.selectbox("종목", list(opts.keys()))
        tk = opts[chosen]; h = hist_data.get(tk)
        if h is None or h.empty:
            st.warning("데이터를 불러올 수 없습니다.")
        else:
            cfig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                row_heights=[0.72, 0.28], vertical_spacing=0.025)
            cfig.add_trace(go.Candlestick(x=h.index,
                open=h["Open"], high=h["High"], low=h["Low"], close=h["Close"], name=chosen,
                increasing_line_color="#0dff8c", decreasing_line_color="#ff3355",
                increasing_fillcolor="#0dff8c", decreasing_fillcolor="#ff3355"), row=1, col=1)
            if len(h)>=20:
                cfig.add_trace(go.Scatter(x=h.index, y=h["Close"].rolling(20).mean(), name="MA20",
                    line=dict(color="#ffd166", width=1.5, dash="dot")), row=1, col=1)
            if len(h)>=60:
                cfig.add_trace(go.Scatter(x=h.index, y=h["Close"].rolling(60).mean(), name="MA60",
                    line=dict(color="#a78bfa", width=1.5, dash="dot")), row=1, col=1)
            vol_c = ["#0dff8c" if c>=o else "#ff3355" for c,o in zip(h["Close"],h["Open"])]
            cfig.add_trace(go.Bar(x=h.index, y=h["Volume"], marker_color=vol_c, opacity=0.7,
                name="거래량", showlegend=False), row=2, col=1)
            cfig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(8,13,24,0.85)",
                font=dict(family="JetBrains Mono", color="#6b7fa3", size=11),
                xaxis_rangeslider_visible=False, height=560, margin=dict(l=0,r=0,t=12,b=0),
                legend=dict(bgcolor="rgba(8,13,24,0.9)", bordercolor="rgba(255,255,255,0.08)",
                    borderwidth=1, font=dict(color="#f0f4ff", size=11)),
                hoverlabel=dict(bgcolor="#0c1220", bordercolor="rgba(255,255,255,0.1)",
                    font=dict(family="JetBrains Mono", size=12)))
            cfig.update_xaxes(showgrid=False, linecolor="rgba(255,255,255,0.05)")
            cfig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.04)")
            st.plotly_chart(cfig, use_container_width=True, config={"displayModeBar":False})

with tab3:
    rows = []
    for n in kr_sel:
        tk=KR_STOCKS[n]; h=hist_data.get(tk); inf=info_data.get(tk,{}); ret=period_return(h)
        mc=inf.get("market_cap")
        rows.append({"국가":"🇰🇷","종목":n,"티커":tk.replace(".KS",""),
            "현재가":fmt_price(inf.get("price"),"KRW"),"수익률":ret,
            "시가총액":f"₩{mc/1e12:.1f}조" if mc else "—"})
    for n in us_sel:
        tk=US_STOCKS[n]; h=hist_data.get(tk); inf=info_data.get(tk,{}); ret=period_return(h)
        mc=inf.get("market_cap")
        rows.append({"국가":"🇺🇸","종목":n,"티커":tk,
            "현재가":fmt_price(inf.get("price"),"USD"),"수익률":ret,
            "시가총액":f"${mc/1e9:.0f}B" if mc else "—"})
    rows.sort(key=lambda x:(x["수익률"] or -9999), reverse=True)

    labels = [f"{r['국가']} {r['종목']}" for r in rows]
    rets   = [r["수익률"] or 0 for r in rows]
    bar_c  = ["#0dff8c" if v>=0 else "#ff3355" for v in rets]

    bfig = go.Figure(go.Bar(
        y=labels[::-1], x=rets[::-1], orientation="h",
        marker=dict(color=bar_c[::-1], line=dict(color="rgba(255,255,255,0.08)", width=0.5)),
        text=[fmt_pct(v) for v in rets[::-1]], textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11, color="#f0f4ff"),
        hovertemplate="<b>%{y}</b><br>%{x:.2f}%<extra></extra>"))
    bfig.add_vline(x=0, line_color="rgba(255,255,255,0.08)", line_width=1)
    bfig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(8,13,24,0.85)",
        font=dict(family="JetBrains Mono", color="#6b7fa3", size=11),
        xaxis=dict(title=f"수익률 ({period_label})", showgrid=True,
            gridcolor="rgba(255,255,255,0.04)", ticksuffix="%", tickfont=dict(size=10)),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#f0f4ff")),
        height=max(360, len(rows)*50), margin=dict(l=0,r=70,t=12,b=0),
        hoverlabel=dict(bgcolor="#0c1220", bordercolor="rgba(255,255,255,0.1)",
            font=dict(family="JetBrains Mono", size=12)))
    st.plotly_chart(bfig, use_container_width=True, config={"displayModeBar":False})

    df = pd.DataFrame(rows)
    df["수익률"] = df["수익률"].apply(fmt_pct)
    df = df.rename(columns={"수익률":f"수익률 ({period_label})"})
    st.dataframe(df[["국가","종목","티커","현재가",f"수익률 ({period_label})","시가총액"]],
        use_container_width=True, hide_index=True)

# ── Correlation ───────────────────────────────────────────────────────────────
if len(all_t) >= 2:
    st.markdown('<div class="sec-label" style="margin-top:1.5rem"><div class="sec-line"></div><span class="sec-text us">🔗 CORRELATION MATRIX</span><div class="sec-line"></div></div>', unsafe_allow_html=True)
    rets_s = {}
    for name, ticker in all_map.items():
        h = hist_data.get(ticker)
        if h is not None and len(h)>5:
            flag = "🇰🇷" if ticker in kr_map.values() else "🇺🇸"
            rets_s[f"{flag} {name}"] = h["Close"].pct_change().dropna()
    if len(rets_s) >= 2:
        corr = pd.DataFrame(rets_s).dropna().corr()
        hfig = go.Figure(go.Heatmap(
            z=corr.values, x=corr.columns.tolist(), y=corr.index.tolist(),
            colorscale=[[0,"#ff3355"],[0.5,"#0c1220"],[1,"#00c6ff"]], zmid=0,
            text=[[f"{v:.2f}" for v in row] for row in corr.values],
            texttemplate="%{text}", textfont=dict(family="JetBrains Mono", size=11, color="#f0f4ff"),
            hovertemplate="%{y} × %{x}<br>r = %{z:.3f}<extra></extra>"))
        hfig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(8,13,24,0.85)",
            font=dict(family="JetBrains Mono", color="#6b7fa3", size=10),
            height=max(320, len(rets_s)*52), margin=dict(l=0,r=0,t=12,b=0),
            xaxis=dict(tickangle=-30, tickfont=dict(size=9, color="#f0f4ff")),
            yaxis=dict(tickfont=dict(size=9, color="#f0f4ff")))
        st.plotly_chart(hfig, use_container_width=True, config={"displayModeBar":False})

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center;padding:1.2rem 0;border-top:1px solid rgba(255,255,255,0.05)'>
  <span style='font-family:JetBrains Mono,monospace;font-size:.68rem;color:#2d3f5a;letter-spacing:.15em'>
    ⚡ STOCKSCOPE · DATA BY YFINANCE · FOR REFERENCE ONLY · NOT FINANCIAL ADVICE
  </span>
</div>""", unsafe_allow_html=True)
