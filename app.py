import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.express as px
import time

st.set_page_config(page_title="539 數據分析大師", layout="wide")
st.title("🍀 今彩 539 即時分析與隔日建議")

# --- 核心抓取邏輯：雙來源備援系統 ---
@st.cache_data(ttl=600)
def fetch_539_data():
    # 來源 A: Lotto-8 (主要來源)
    # 來源 B: 樂透雲 (備用來源)
    sources = [
        "https://www.lotto-8.com/list539.asp",
        "https://www.lotto-cloud.com/list539.aspx"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }

    for url in sources:
        try:
            res = requests.get(url, headers=headers, timeout=15)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                lotto_data = []
                
                # 針對 Lotto-8 的解析邏輯
                if "lotto-8" in url:
                    rows = soup.find_all('tr', class_=['list_tr1', 'list_tr2'])
                    for row in rows:
                        tds = row.find_all('td')
                        if len(tds) >= 3:
                            nums = [int(n) for n in tds[2].get_text(separator=' ').strip().replace('\xa0', ' ').split() if n.isdigit()]
                            if len(nums) == 5: lotto_data.append(nums)
                
                # 如果有抓到資料就回傳，不繼續嘗試下一個來源
                if lotto_data:
                    return pd.DataFrame(lotto_data, columns=['n1', 'n2', 'n3', 'n4', 'n5'])
        except:
            continue # 如果當前來源失敗，嘗試下一個
            
    return pd.DataFrame()

# 執行抓取
with st.spinner('正在與開獎中心同步數據...'):
    df = fetch_539_data()

if not df.empty:
    # 顯示最新獎號
    latest = df.iloc[0]
    st.success(f"📅 最新一期獎號：{' , '.join([f'{n:02d}' for n in latest])}")
    
    # 數據視覺化
    all_nums = df.values.flatten()
    counts = Counter(all_nums)
    stat_df = pd.DataFrame([{"號碼": i, "次數": counts.get(i, 0)} for i in range(1, 40)])
    
    st.header("📊 近期 50 期號碼熱度統計")
    fig = px.bar(stat_df, x='號碼', y='次數', color='次數', text_auto=True, color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

    # 分析建議
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔥 熱門強勢號")
        hot_nums = [f"{n:02d}" for n, c in Counter(all_nums).most_common(5)]
        st.info(f"建議：{', '.join(hot_nums)}")
    with c2:
        st.subheader("❄️ 冷門回歸號")
        cold_nums = [f"{n:02d}" for n, c in sorted(counts.items(), key=lambda x: x[1])[:5]]
        st.warning(f"建議：{', '.join(cold_nums)}")
else:
    st.error("目前所有開獎來源連線繁忙。請點擊上方三點選單選擇 'Clear cache' 後再 'Rerun'。")
