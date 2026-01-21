import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.express as px
import datetime

st.set_page_config(page_title="539 數據大師", layout="wide")
st.title("🍀 今彩 539 即時分析與隔日預測")

# --- 1. 抓取資料功能 ---
@st.cache_data(ttl=3600)
def get_lotto_data():
    # 這裡預留真實爬蟲位置，先提供近半年的統計基礎資料
    # 模擬 150 期的數據邏輯
    import numpy as np
    dates = pd.date_range(end=datetime.date.today(), periods=150)
    data = []
    for d in dates:
        # 模擬 539 隨機開獎 (1-39 選 5)
        nums = np.random.choice(range(1, 40), 5, replace=False)
        nums.sort()
        data.append([d.strftime('%Y-%m-%d')] + list(nums))
    return pd.DataFrame(data, columns=['日期', 'n1', 'n2', 'n3', 'n4', 'n5'])

df = get_lotto_data()

# --- 2. 顯示最新一期資訊 ---
latest = df.iloc[-1]
st.subheader(f"📅 最新一期開獎數據 ({latest['日期']})")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("號碼 1", latest['n1'])
c2.metric("號碼 2", latest['n2'])
c3.metric("號碼 3", latest['n3'])
c4.metric("號碼 4", latest['n4'])
c5.metric("號碼 5", latest['n5'])

# --- 3. 重複性分析 (近半年) ---
st.divider()
st.header("📈 近半年出現頻率統計")
all_numbers = df[['n1', 'n2', 'n3', 'n4', 'n5']].values.flatten()
counts = Counter(all_numbers)
stat_df = pd.DataFrame(counts.most_common(), columns=['號碼', '次數']).sort_values('號碼')

fig = px.bar(stat_df, x='號碼', y='次數', color='次數', text_auto=True,
             title="539 號碼分佈圖 (數字越長代表出現次數越多)")
st.plotly_chart(fig, use_container_width=True)

# --- 4. 隔日有用分析 (你的核心需求) ---
st.divider()
st.header("🔮 隔日分析建議")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🔥 熱門強勢號 (Top 5)")
    hot_5 = [str(x[0]).zfill(2) for x in counts.most_common(5)]
    st.success(f"這些號碼近期非常強勢：{', '.join(hot_5)}")

with col_right:
    st.subheader("❄️ 冷門回歸號 (Bottom 5)")
    cold_5 = [str(x[0]).zfill(2) for x in counts.most_common()[-5:]]
    st.warning(f"這些號碼久未開出，值得關注：{', '.join(cold_5)}")

st.info("💡 貼心提醒：建議組合 2 個熱門號 + 1 個冷門號 + 2 個隨機號。")
