import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.express as px

st.set_page_config(page_title="539 數據分析大師", layout="wide")
st.title("🍀 今彩 539 即時分析與隔日建議")

# --- 自動抓取真實數據的功能 ---
@st.cache_data(ttl=3600) # 每小時自動更新數據
def fetch_real_539_data():
    url = "https://www.lotto-8.com/list539.asp"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 抓取表格中的開獎號碼 (前 50 期)
        all_rows = soup.find_all('tr', class_=['list_tr1', 'list_tr2'])
        lotto_data = []
        for row in all_rows:
            tds = row.find_all('td')
            if len(tds) >= 3:
                nums_text = tds[2].text.strip().replace('\xa0', ' ')
                nums = [int(n) for n in nums_text.split() if n.isdigit()]
                if len(nums) == 5:
                    lotto_data.append(nums)
        return pd.DataFrame(lotto_data, columns=['n1', 'n2', 'n3', 'n4', 'n5'])
    except:
        return pd.DataFrame()

# 執行抓取
with st.spinner('正在從網路獲取最新 539 獎號...'):
    df = fetch_real_539_data()

if not df.empty:
    # 1. 顯示最新一期
    st.subheader(f"📅 最新開獎結果：{', '.join([f'{n:02d}' for n in df.iloc[0]])}")
    
    # 2. 統計分析 (重複性)
    st.divider()
    all_nums = df.values.flatten()
    counts = Counter(all_nums)
    stat_df = pd.DataFrame(counts.most_common(), columns=['號碼', '次數']).sort_values('號碼')
    
    st.header("📊 近期號碼熱度統計")
    fig = px.bar(stat_df, x='號碼', y='次數', color='次數', text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    # 3. 隔日分析建議
    st.divider()
    st.header("🔮 隔日有用分析建議")
    c1, c2 = st.columns(2)
    with c1:
        st.success(f"🔥 熱門強勢號 (Top 5)：\n{', '.join([f'{n:02d}' for n, c in counts.most_common(5)])}")
    with c2:
        # 找出近期最冷門的 5 個號碼
        cold_5 = [f'{n:02d}' for n, c in sorted(counts.items(), key=lambda item: item[1])[:5]]
        st.warning(f"❄️ 冷門回歸號 (Bottom 5)：\n{', '.join(cold_5)}")
else:
    st.error("目前無法獲取網路數據，請稍後再試。")
