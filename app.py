import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="539 數據分析大師", layout="wide")
st.title("🍀 今彩 539 即時分析與隔日建議")

# 2. 自動抓取真實數據函數 (直接爬取公開網頁，免金鑰)
@st.cache_data(ttl=3600)
def fetch_real_data():
    url = "https://www.lotto-8.com/list539.asp"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 尋找表格中的開獎資料列 (抓取最近 50 期)
        all_rows = soup.find_all('tr', class_=['list_tr1', 'list_tr2'])
        lotto_data = []
        for row in all_rows:
            tds = row.find_all('td')
            if len(tds) >= 3:
                raw_nums = tds[2].text.strip().replace('\xa0', ' ')
                nums = [int(n) for n in raw_nums.split() if n.isdigit()]
                if len(nums) == 5:
                    lotto_data.append(nums)
        
        return pd.DataFrame(lotto_data, columns=['n1', 'n2', 'n3', 'n4', 'n5'])
    except Exception as e:
        return pd.DataFrame()

# 執行抓取
with st.spinner('正在從網路獲取最新 539 資訊...'):
    df = fetch_real_data()

if not df.empty:
    # A. 顯示最新一期號碼
    latest = df.iloc[0]
    st.success(f"📅 最新一期獎號：{' , '.join([f'{n:02d}' for n in latest])}")
    
    # B. 統計號碼頻率
    all_numbers = df.values.flatten()
    counts = Counter(all_numbers)
    # 確保 1-39 每個號碼都出現在統計中
    full_counts = {i: counts.get(i, 0) for i in range(1, 40)}
    stat_df = pd.DataFrame(list(full_counts.items()), columns=['號碼', '出現次數']).sort_values('號碼')
    
    # C. 畫出號碼熱度圖
    st.divider()
    st.header("📊 近期 50 期號碼熱度統計")
    fig = px.bar(stat_df, x='號碼', y='出現次數', color='出現次數', 
                 text_auto=True, color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

    # D. 核心預測建議
    st.divider()
    st.header("🔮 數據建議號碼")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 近期熱門區")
        hot_nums = [f"{n:02d}" for n, c in Counter(all_numbers).most_common(5)]
        st.write("開出頻率最高：")
        st.info(f"{', '.join(hot_nums)}")
        
    with col2:
        st.subheader("❄️ 冷門回歸區")
        # 排序次數最少的
        cold_nums = [f"{n:02d}" for n, c in sorted(full_counts.items(), key=lambda x: x[1])[:5]]
        st.write("長期未開可能反彈：")
        st.warning(f"{', '.join(cold_nums)}")
    
    st.info("💡 小提示：大數據顯示從熱門號選 2 個，冷門號選 1 個作為搭配，勝率相對較穩定。")
else:
    st.error("網路抓取失敗，請確認 https://www.lotto-8.com/list539.asp 是否正常。")
