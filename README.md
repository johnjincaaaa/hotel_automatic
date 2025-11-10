# 酒店价格爬虫工具使用说明

## 项目简介
`hotel_automatic` 是一个基于 Selenium 的酒店价格自动化爬取工具，支持通过上传包含酒店网址的 Excel/CSV 文件，批量抓取多个酒店平台的价格信息，并提供结果下载功能。目前已支持 `trip.com` 和 `booking.com` 两个平台的解析。

## 功能特点
- 支持上传 Excel/CSV 格式的酒店网址文件
- 自动识别不同平台（trip.com、booking.com）并使用对应解析规则
- 模拟人工浏览行为（随机滚动、延时），降低反爬风险
- 实时显示抓取进度，支持结果预览
- 提供 Excel 和 CSV 格式的结果下载

## 环境要求
- Python 3.7+
- 依赖库：`streamlit`、`pandas`、`selenium`、`openpyxl`
- Chrome 浏览器及对应版本的 `chromedriver`（需配置正确路径）

## 安装步骤
1. 克隆或下载项目代码
2. 安装依赖包：
```bash
pip install streamlit pandas selenium openpyxl
```
3. 下载与本地 Chrome 浏览器版本匹配的 `chromedriver`，并在 `main.py` 中修改驱动路径：
```python
service = Service(r"你的chromedriver路径")  # 例如：r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"
```

## 使用方法
1. 运行程序：
```bash
streamlit run main.py
```
2. 在网页界面中：
   - **步骤1**：上传包含「酒店网址」列的 Excel/CSV 文件
   - **步骤2**：点击「开始批量抓取」按钮，等待抓取完成
   - **步骤3**：下载 Excel 或 CSV 格式的抓取结果

## 注意事项
1. 确保网络连接稳定，抓取过程中请勿关闭浏览器窗口
2. 不同平台的网页结构可能会更新，若出现抓取失败请检查解析规则是否需要调整
3. 频繁抓取可能导致 IP 被临时限制，建议合理控制抓取频率
4. `booking.txt` 中包含部分网站 Cookie 信息，用于辅助模拟正常浏览行为

## 扩展说明
如需支持更多酒店平台，可在 `main.py` 的 `crawl_hotel_price` 函数中添加新的解析逻辑：
```python
elif "新平台域名" in url:
    # 添加对应平台的元素定位和解析代码
    hotel_name = driver.find_elements(By.XPATH, '//对应的XPath')
    price = driver.find_elements(By.XPATH, '//对应的XPath')
    # 处理数据并添加到结果列表
```

## 常见问题
- **文件读取失败**：检查文件格式是否正确，是否包含「酒店网址」列
- **抓取失败**：检查网络连接、chromedriver 路径是否正确，或目标网站是否有反爬机制
- **价格为空**：可能是网页结构更新导致解析规则失效，需调整对应 XPath 表达式
