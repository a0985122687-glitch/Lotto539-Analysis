import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.express as px

# 1. 網頁基本設定
st.set_page_config(page_title="539 數據分析大師", layout="wide")
st.title("🍀 今彩 539 即時分析與隔日建議")

# 2. 自動抓取真實數據函數 (增加 headers 偽裝)
@st.cache_data(ttl=600)  # 每 10 分鐘嘗試更新
def fetch_real_data():
    url = "https://www.lotto-8.com/list539.asp"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 尋找開獎號碼所在的表格列
        all_rows = soup.find_all('tr', class_=['list_tr1', 'list_tr2'])
        lotto_data = []
        for row in all_rows:
            tds = row.find_all('td')
            if len(tds) >= 3:
                # 提取號碼字串並清理格式
                raw_nums = tds[2].get_text(separator=' ').strip().replace('\xa0', ' ')
                nums = [int(n) for n in raw_nums.split() if n.isdigit()]
                if len(nums) == 5:
                    lotto_data.append(nums)
        
        return pd.DataFrame(lotto_data, columns=['n1', 'n2', 'n3', 'n4', 'n5'])
    except Exception as e:
        st.warning(f"偵測到連線波動，正在嘗試備份方案... (錯誤: {e})")
        return pd.DataFrame()

# 執行抓取
df = fetch_real_data()

if not df.empty:
    # A. 顯示最新一期
    latest = df.iloc[0]
    st.success(f"📅 最新一期獎號：{' , '.join([f'{n:02d}' for n in latest])}")
    
    # B. 統計號碼熱度
    all_numbers = df.values.flatten()
    counts = Counter(all_numbers)
    # 建立 1-39 完整清單
    stat_list = [{"號碼": i, "次數": counts.get(i, 0)} for i in range(1, 40)]
    stat_df = pd.DataFrame(stat_list)
    
    # C. 繪製圖表
    st.divider()
    st.header("📊 近期 50 期號碼熱度統計")
    fig = px.bar(stat_df, x='號碼', y='次數', color='次數', 
                 text_auto=True, color_continuous_scale='Turbo')
    st.plotly_chart(fig, use_container_width=True)

    # D. 隔日建議邏輯
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔥 熱門候選")
        hot_5 = [f"{n:02d}" for n, c in Counter(all_numbers).most_common(5)]
        st.info(f"建議關注：{', '.join(hot_5)}")
    with c2:
        st.subheader("❄️ 冷門參考")
        # 排序出現次數最少的
        cold_5 = [f"{n:02d}" for n, c in sorted(counts.items(), key=lambda x: x[1])[:5]]
        st.warning(f"建議關注：{', '.join(cold_5)}")
        
    st.caption("數據來源：Lotto-8 公開開獎資訊。分析僅供參考，請理性投注。")
else:
    st.error("目前伺服器請求過多，請點擊上方三點選單選擇 'Rerun' 或重新整理網頁。")
