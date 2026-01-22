import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="539 數據分析大師", layout="wide")
st.title("🍀 今彩 539 即時開獎分析與隔日建議")

# 2. 自動抓取資料功能
@st.cache_data(ttl=3600) # 每小時更新一次，避免被封鎖
def fetch_539_data():
    # 抓取來源：常用的開獎統計網站
    url = "https://www.lotto-8.com/list539.asp"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 找到包含開獎號碼的表格
        # 這裡會抓取網頁上最近期的 50 筆資料
        all_rows = soup.find_all('tr', class_='list_tr1') + soup.find_all('tr', class_='list_tr2')
        
        lotto_list = []
        for row in all_rows:
            tds = row.find_all('td')
            if len(tds) >= 3:
                # 提取號碼文字並轉成數字清單
                nums_text = tds[2].text.strip()
                nums = [int(n) for n in nums_text.replace('\xa0', ' ').split()]
                if len(nums) == 5:
                    lotto_list.append(nums)
        
        return pd.DataFrame(lotto_list, columns=['n1', 'n2', 'n3', 'n4', 'n5'])
    except Exception as e:
        st.error(f"資料抓取失敗: {e}")
        return pd.DataFrame()

# 執行抓取
with st.spinner('正在連線台灣彩券資訊庫...'):
    df = fetch_539_data()

if not df.empty:
    # 3. 顯示最新一期號碼
    latest = df.iloc[0]
    st.subheader("📅 最新一期開獎號碼")
    cols = st.columns(5)
    for i, col in enumerate(cols):
        col.metric(f"號碼 {i+1}", f"{latest[f'n{i+1}']:02d}")

    # 4. 統計近半年重複性 (以現有抓到的資料為準)
    st.divider()
    st.header("📊 號碼出現頻率統計")
    all_numbers = df.values.flatten()
    counts = Counter(all_numbers)
    
    # 建立統計表
    stat_df = pd.DataFrame(counts.most_common(), columns=['號碼', '出現次數']).sort_values('號碼')
    
    # 圖表呈現
    fig = px.bar(stat_df, x='號碼', y='出現次數', color='出現次數', text_auto=True,
                 title="近期 50 期號碼熱度圖")
    st.plotly_chart(fig, use_container_width=True)

    # 5. 隔日有用分析 (核心預測邏輯)
    st.divider()
    st.header("🔮 隔日有用分析建議")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🔥 熱門強勢號 (Top 5)")
        hot_5 = [f"{n:02d}" for n, c in counts.most_common(5)]
        st.success(f"近期開出機率最高： {', '.join(hot_5)}")
        
    with col_b:
        st.subheader("❄️ 冷門回歸號 (Bottom 5)")
        # 找出 1-39 中出現次數最少的
        all_possible = set(range(1, 40))
        seen_nums = set(counts.keys())
        missing = list(all_possible - seen_nums)
        cold_5 = [f"{n:02d}" for n in (missing + [n for n, c in reversed(counts.most_common())])[:5]]
        st.warning(f"長期未開值得關注： {', '.join(cold_5)}")

    st.info("💡 數據邏輯：系統會自動計算最近 50 期的開獎分佈。建議投注時可由熱門號中選 2 個，冷門號選 1 個作為搭配。")
else:
    st.warning("目前無法取得即時資料，請確認網路連線。")

st.caption("程式夥伴：本分析僅供數據參考，祝您幸運中獎！")
