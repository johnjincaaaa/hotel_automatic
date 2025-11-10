import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



chrome_options = Options()
# 增强反检测设置
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 新增参数
chrome_options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')  # 模拟正常浏览器UA
chrome_options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
# chrome_options.add_argument("--headless")


# ---------------------- 1. 网页界面配置（Streamlit） ----------------------
st.title("酒店价格爬虫工具")
st.subheader("步骤1：上传酒店网址文件（Excel/CSV）")
# 上传文件（支持Excel和CSV）
uploaded_file = st.file_uploader("请上传含「酒店网址」列的文件", type=["xlsx", "csv"])

# 存储抓取结果的全局变量
result_data = []


# ---------------------- 2. 爬虫核心函数（Playwright） ----------------------
def crawl_hotel_price(url) ->list:


    try:
        # 初始化 Chrome 驱动（需先下载对应版本的 chromedriver，放入项目目录）
        service = Service(r"C:\Program Files\Google\Chrome\Application\chromedriver.exe")  # 替换为你的 chromedriver 路径
        driver = webdriver.Chrome(service=service,options=chrome_options)
        wait = WebDriverWait(driver, 20,poll_frequency=0.5)
        driver.get(url)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = []

        def scroll_to_load_all():
            last_height = driver.execute_script(
                "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
            )  # 获取初始页面高度（兼容不同网页布局）
            scroll_count = 0
            max_scroll = 60  # 最大滚动次数（防止无限循环）
            while scroll_count < max_scroll:
                # 滚动到当前页面底部
                driver.execute_script(
                    "window.scrollTo(0, Math.max(document.body.scrollHeight, document.documentElement.scrollHeight));"
                )
                # 随机等待1-3秒（模拟人工浏览，避免被反爬）
                time.sleep(random.uniform(2, 4))
                # 获取新的页面高度
                new_height = driver.execute_script(
                    "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"
                )
                # # 若高度不变，说明没有新数据加载，停止滚动
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_count += 1


        # 解析逻辑
        if "trip.com" in url:
            wait.until(EC.presence_of_element_located((By.XPATH, r'//div[@class="list-card-title"]/a')))
            scroll_to_load_all()

            hotel_name = driver.find_elements(By.XPATH, '//div[@class="list-card-title"]/a')
            price = driver.find_elements(By.XPATH, '//div[@id="meta-real-price"]/span/div')
            for i_,j_ in zip(hotel_name,price):
                i_ = i_.text
                j_ = j_.text
                data.append({"酒店名": i_, "价格": j_, "抓取时间戳": timestamp, "酒店网址": url})

        elif "booking.com" in url:
            # 点击操作1：等待元素可点击后再点击
            wait.until(EC.presence_of_element_located((By.XPATH, r'//span[@aria-hidden="true"]'))).click()

            # 点击操作2：同上
            wait.until(EC.element_to_be_clickable((By.XPATH, r'//button[@type="button"]'))).click()

            # 处理cookie弹窗（常见场景，确保弹窗出现后再点击）
            try:
                wait.until(
                    EC.presence_of_element_located((By.XPATH, r'//button[@id="onetrust-accept-btn-handler"]'))).click()
            except LookupError as e:
                print(e)
            # 关闭登录信息弹窗
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, r'//button[@aria-label="关闭登录信息。"]'))).click()
            except LookupError as e:
                print(e)
            wait.until(EC.presence_of_element_located((By.XPATH, r'//div[@data-testid="title"]')))
            scroll_to_load_all()
            hotel_name = driver.find_elements(By.XPATH, r'//div[@data-testid="title"]')
            price = driver.find_elements(By.XPATH, r'//span[@data-testid="price-and-discounted-price"]')
            for i_,j_ in zip(hotel_name,price):
                i_ = i_.text
                j_ = j_.text
                data.append({"酒店名": i_, "价格": j_, "抓取时间戳": timestamp, "酒店网址": url})

        # elif '....' in url: 可继续添加域名
        #     hotel_name = ....
        #     price = ....

        else:
            hotel_name = "未知平台"
            price = "未匹配解析规则"
            data.append({"酒店名": hotel_name, "价格": price, "抓取时间戳": timestamp, "酒店网址": url})

        driver.quit()
        return data
    except Exception as e:
        return [{"酒店名": "抓取失败", "价格": f"错误：{str(e)}",
                "抓取时间戳": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "酒店网址": url}]

# ---------------------- 3. 批量抓取逻辑 ----------------------
if uploaded_file is not None:
    # 读取上传的文件，提取「酒店网址」列
    try:
        if uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:  # CSV
            df = pd.read_csv(uploaded_file)

        # 验证文件是否含「酒店网址」列
        if "酒店网址" not in df.columns:
            st.error("文件缺少「酒店网址」列，请检查文件格式！")
        else:
            hotel_urls = df["酒店网址"].dropna().tolist()  # 去除空值，获取网址列表
            st.success(f"成功读取 {len(hotel_urls)} 个酒店网址")

            # 显示「开始抓取」按钮
            if st.button("步骤2：开始批量抓取"):
                with st.spinner("正在批量抓取，请稍候..."):
                    # 进度条
                    progress_bar = st.progress(0)
                    result_data = []

                    # 逐个抓取每个网址
                    for i, url in enumerate(hotel_urls):
                        results :list= crawl_hotel_price(url)
                        for result in results:
                            result["酒店网址"] = url  # 补充原网址到结果中
                            result_data.append(result)
                        # 更新进度条
                        progress_bar.progress((i + 1) / len(hotel_urls))

                    # 转换结果为DataFrame，显示在网页上
                    result_df = pd.DataFrame(result_data)
                    st.subheader("抓取结果预览")
                    st.dataframe(result_df)
    # 补充except块，捕获文件读取异常
    except Exception as e:
        st.error(f"文件读取失败：{str(e)}")

# ---------------------- 4. 结果下载功能 ----------------------
if len(result_data) > 0:
    result_df = pd.DataFrame(result_data)
    # 生成Excel文件（支持下载）
    excel_buffer = pd.ExcelWriter("酒店价格抓取结果.xlsx", engine="openpyxl")
    result_df.to_excel(excel_buffer, index=False, sheet_name="抓取结果")
    excel_buffer.close()

    # 读取Excel文件为二进制流，用于下载
    with open("酒店价格抓取结果.xlsx", "rb") as f:
        excel_bytes = f.read()

    # 生成CSV文件（支持下载）
    csv_bytes = result_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8")

    # 显示下载按钮
    st.subheader("步骤3：下载抓取结果")
    st.download_button(
        label="下载Excel格式",
        data=excel_bytes,
        file_name=f"酒店价格抓取结果_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.download_button(
        label="下载CSV格式",
        data=csv_bytes,
        file_name=f"酒店价格抓取结果_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )