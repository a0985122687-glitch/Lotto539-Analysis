import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.express as px

st.set_page_config(page_title="539 分析大師", layout="wide")
st.title("🍀 今彩 539 即時數據分析")

# --- 抓取真實數據的函數 ---
@st.cache_data(ttl=3600)
def fetch_real_data():
    # 這裡我們先建立一個穩定的數據抓取邏輯
    # 暫時用模擬數據確保你能成功部署，成功後我再教你更換精準爬蟲網址
    import numpy as np
    data = []
    for i in range(100):
        nums = np.random.choice(range(1, 40), 5, replace=False)
        nums.sort()
        data.append(nums)
    return pd.DataFrame(data, columns=['n1', 'n2', 'n3', 'n4', 'n5'])

df = fetch_real_data()

# --- 介面呈現 ---
st.header("📊 近期號碼出現頻率")
all_nums = df.values.flatten()
counts = Counter(all_nums)
stat_df = pd.DataFrame(counts.most_common(), columns=['號碼', '次數']).sort_values('號碼')

fig = px.bar(stat_df, x='號碼', y='次數', color='次數', title="號碼熱度圖")
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.header("🔮 隔日有用分析")
hot_nums = [str(x[0]).zfill(2) for x in counts.most_common(5)]
st.success(f"🔥 近期熱門建議：{', '.join(hot_nums)}")
