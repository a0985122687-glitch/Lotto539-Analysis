import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import Counter
import plotly.express as px
import time

# 頁面設定
st.set_page_config(page_title="539 數據分析大師", layout="wide")
st.title("🍀 今彩 539 即時分析與隔日預測")

# 穩定版抓取函數
@st.cache_data(ttl=21600) # 每 6 小時才去抓一次，避開擁塞，資料會存在快取
def fetch_539_data_stable():
    # 這裡選擇穩定性較高的資料來源
    url = "https://www.lotto-8.com/list539.asp"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1'
    }
    
    for i in range(3): # 失敗會自動重試 3 次
        try:
            res = requests.get(url, headers=headers, timeout=20)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                rows = soup.find_all('tr', class_=['list_tr1', 'list_tr2'])
                lotto_data = []
                for row in rows:
                    tds = row.find_all('td')
                    if len(tds) >= 3:
                        # 清理文字與特殊符號
                        n_text = tds[2].get_text(separator=' ').replace('\xa0', ' ').strip()
                        nums = [int(n) for n in n_text.split() if n.isdigit()]
                        if len(nums) == 5: lotto_data.append(nums)
                if lotto_data:
                    return pd.DataFrame(lotto_data, columns=['n1', 'n2', 'n3', 'n4', 'n5'])
        except Exception as e:
            time.sleep(3) # 停頓 3 秒再試
            continue
    return pd.DataFrame()

# 執行
with st.spinner('正在獲取最新數據，請稍候...'):
    df = fetch_539_data_stable()

if not df.empty:
    # 1. 顯示最新一期
    latest = df.iloc[0]
    st.success(f"📅 最新開獎結果：{' , '.join([f'{n:02d}' for n in latest])}")

    # 2. 畫熱度圖
    all_nums = df.values.flatten()
    counts = Counter(all_nums)
    stat_df = pd.DataFrame([{"號碼": i, "次數": counts.get(i, 0)} for i in range(1, 40)])
    
    st.header("📊 近期 50 期出現頻率統計")
    fig = px.bar(stat_df, x='號碼', y='次數', color='次數', text_auto=True, color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)

    # 3. 隔日有用分析
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔥 熱門強勢號 (推薦選 2)")
        hot = [f"{n:02d}" for n, c in Counter(all_nums).most_common(5)]
        st.info(", ".join(hot))
    with c2:
        st.subheader("❄️ 冷門回歸號 (推薦選 1)")
        # 找出次數最少的
        cold = [f"{n:02d}" for n, c in sorted(counts.items(), key=lambda x:x[1])[:5]]
        st.warning(", ".join(cold))
        
    st.caption(f"最後更新時間：{time.strftime('%Y-%m-%d %H:%M:%S')}")
else:
    st.error("目前開獎網站連線過於擁塞。建議您在非開獎尖峰時段（例如下午）再行查看。")
    if st.button("點擊手動重試"):
        st.cache_data.clear()
        st.rerun()
