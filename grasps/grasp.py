"""
Project: AIStock
Creator: Jiacheng Xu
Create time: 2021-02-24 10:11
IDE: PyCharm
Introduction:
"""
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains

details = []

## 启动浏览器
driver = webdriver.Chrome('./chromedriver', )
driver.set_window_size(1440, 960)             # 设置浏览器界面

driver.get('http://data.eastmoney.com/cjsj/newhouse.html')

for j in range(3, 8):
    ## 点击到 指定 页
    driver.find_element_by_xpath('//*[@id="gotopageindex"]').send_keys(webdriver.common.keys.Keys.BACKSPACE)
    driver.find_element_by_xpath('//*[@id="gotopageindex"]').send_keys(f'{j}')
    driver.find_element_by_xpath('//*[@id="cjsj_table_pager"]/div[2]/form/input[2]').click()
    time.sleep(0.5)

    for i in range(1, 40 if j < 7 else 2 , 2):
        ## 点击详细数据页面
        web_element = driver.find_element_by_xpath(f'//*[@id="cjsj_table"]/table/tbody/tr[{i}]/td[12]/a')
        ActionChains(driver).move_to_element(web_element).perform()
        ActionChains(driver).click(web_element).perform()
        time.sleep(0.5)

        ## 解析数据
        detail = []
        cnt = 0
        while not detail:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            detail = soup.select('.modal .table-model tr')
            cnt += 1
            time.sleep(0.1)
            if cnt > 3:
                break

        details += detail

        ## 关闭页面
        driver.find_element_by_xpath('/html/body/div[7]/div[2]/div[1]/span').click()


## 处理数据
data = '日期,城市,新建住宅环比,新建住宅同比,新建住宅定基,新建商品房环比,新建商品房同比,新建商品房定基,二手住宅环比,二手住宅同比,二手住宅定基\n'
for det in details:
    dd = det.select('td')
    if dd:
        data += ','.join([f.text for f in dd]) + '\n'

## 保存数据
with open('house_index.csv', 'w') as file:
    file.writelines(data)