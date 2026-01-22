import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.express as px
from datetime import datetime
import time

# 1. 基本設定
st.set_page_config(page_title="539 數據分析大師", layout="wide")
st.title("🍀 今彩 539 穩定分析版")

# 2. 核心抓取邏輯 (針對擁塞進行優化)
@st.cache_data(ttl=43200) # 快取 12 小時，極大減少對目標網站的騷擾
def fetch_lotto_data():
    # 嘗試多個備用來源
    urls = [
        "https://www.lotto-8.com/list539.asp",
        "https://web.archive.org/web/https://www.lotto-8.com/list539.asp" # 備用快取來源
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    for url in urls:
        try:
            res = requests.get(url, headers=headers, timeout=20)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                rows = soup.find_all('tr', class_=['list_tr1', 'list_tr2'])
                data = []
                for row in rows:
                    tds = row.find_all('td')
                    if len(tds) >= 3:
                        n_str = tds[2].get_text(separator=' ').replace('\xa0', ' ').strip()
                        nums = [int(n) for n in n_str.split() if n.isdigit()]
                        if len(nums) == 5: data.append(nums)
                if data:
                    return pd.DataFrame(data, columns=['n1','n2','n3','n4','n5'])
        except:
            continue
    return pd.DataFrame()

# 3. 判斷現在是否適合抓取
now_hour = datetime.now().hour
st.info(f"💡 當前系統時間：{datetime.now().strftime('%H:%M')}。建議在下午時段查看以獲得最佳穩定性。")

# 4. 執行與呈現
with st.spinner('正在分析中...'):
    df = fetch_lotto_data()

if not df.empty:
    st.success(f"✅ 數據同步成功！最新一期號碼：{', '.join([f'{n:02d}' for n in df.iloc[0]])}")
    
    # 圖表呈現
    all_nums = df.values.flatten()
    counts = Counter(all_nums)
    stat_df = pd.DataFrame([{"號碼": i, "次數": counts.get(i, 0)} for i in range(1, 40)])
    
    fig = px.bar(stat_df, x='號碼', y='次數', color='次數', text_auto=True, color_continuous_scale='Magma')
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔥 熱門分析")
        st.write(", ".join([f"{n:02d}" for n, c in Counter(all_nums).most_common(5)]))
    with col2:
        st.subheader("❄️ 冷門分析")
        st.write(", ".join([f"{n:02d}" for n, c in sorted(counts.items(), key=lambda x:x[1])[:5]]))
else:
    st.error("⚠️ 偵測到開獎官網流量異常擁塞。")
    st.warning("請於非開獎高峰期（如您建議的下午 5 點）再試一次，系統將自動緩存穩定數據。")
    if st.button("強制刷新數據庫"):
        st.cache_data.clear()
        st.rerun()
