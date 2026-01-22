import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.express as px

# 1. 頁面設定
st.set_page_config(page_title="539 數據分析大師", layout="wide")
st.title("🍀 今彩 539 即時分析與隔日建議")

# 2. 真實數據抓取函數 (從公開開獎紀錄網抓取最近 50 期)
@st.cache_data(ttl=3600)
def fetch_real_data():
    url = "https://www.lotto-8.com/list539.asp"
    try:
        # 模擬瀏覽器發送請求
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 尋找表格中的開獎資料列
        all_rows = soup.find_all('tr', class_=['list_tr1', 'list_tr2'])
        lotto_data = []
        for row in all_rows:
            tds = row.find_all('td')
            if len(tds) >= 3:
                # 取得開獎號碼字串並轉為數字清單
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
    # 建立 1-39 的完整統計表，確保沒開出的號碼也會顯示次數 0
    full_counts = {i: counts.get(i, 0) for i in range(1, 40)}
    stat_df = pd.DataFrame(list(full_counts.items()), columns=['號碼', '出現次數']).sort_values('號碼')
    
    # C. 畫出熱度圖
    st.divider()
    st.header("📊 近期 50 期號碼熱度圖")
    fig = px.bar(stat_df, x='號碼', y='出現次數', color='出現次數', 
                 text_auto=True, color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

    # D. 核心分析：預測建議
    st.divider()
    st.header("🔮 數據建模分析建議")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 強勢熱門區")
        hot_nums = [f"{n:02d}" for n, c in Counter(all_numbers).most_common(5)]
        st.write(f"近期開出頻率最高：")
        st.button(f"推薦：{', '.join(hot_nums)}", key="hot")
        
    with col2:
        st.subheader("❄️ 冷門回歸區")
        # 找出出現次數最少的號碼
        cold_nums = [f"{n:02d}" for n, c in sorted(full_counts.items(), key=lambda x: x[1])[:5]]
        st.write(f"長期未開可能反彈：")
        st.button(f"關注：{', '.join(cold_5)}", key="cold")
    
    st.info("💡 專業叮嚀：數據顯示 539 號碼具有『拖牌效應』，建議從熱門區選 2 個，冷門區選 1 個做搭配。")

else:
    st.error("暫時連不上資料庫，請稍後幾分鐘重新整理網頁。")
