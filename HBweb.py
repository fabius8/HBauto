# -*- encoding=utf8 -*-
__author__ = "fabiu"

from airtest.core.api import *

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.keys import Keys
from airtest_selenium.proxy import WebChrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import pyotp
import json
import sys


pointhbjson = json.load(open('point_hb.json'))

number = -1
print(sys.argv)
if len(sys.argv) >= 2:
    print(sys.argv[1])
    number = int(sys.argv[1])
else:
    print("please input number")
    sleep(5)
    sys.exit()

if number < 1 or number > 235:
    sleep(5)
    sys.exit()
    
choose = pointhbjson[number]
print(choose["Username"], choose["Password"], choose["Secret"])

opt = Options()
opt.add_argument("--user-data-dir=C:\\Users\\fabiu\\AppData\\Local\\Google\\Chrome\\User Data\\" + str(number))
#opt.add_argument("--remote-debugging-port=9222")
opt.add_argument("--start-maximized")
opt.add_experimental_option('excludeSwitches', ['enable-automation'])
opt.add_experimental_option('useAutomationExtension', False)
opt.add_argument("--disable-blink-features=AutomationControlled")

driver = WebChrome(ChromeDriverManager().install(), options=opt)

with open('./stealth.min.js') as f:
    js = f.read()
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": js
})

driver.implicitly_wait(10)

driver.get("https://www.huobi.com/en-us/finance/account/spot")
driver.find_element_by_xpath("//input[@type='text']").send_keys(Keys.CONTROL, "a")
driver.find_element_by_xpath("//input[@type='text']").send_keys(choose["Username"])
driver.find_element_by_id("password").send_keys(Keys.CONTROL, "a")
driver.find_element_by_id("password").send_keys(choose["Password"])
driver.find_element_by_xpath("//button[@class='login-btn-submit']").click()
sleep(2)

driver.implicitly_wait(5)
try:
    while driver.find_element_by_xpath("//div[@id='alicaptcha-1']").get_attribute('style') == "display: none;":
        print("good test not come")
        driver.find_element_by_xpath("//a[@class='switch-btn']").click()
    sleep(2)
    action = ActionChains(driver)
    block = driver.find_element_by_id("nc_1_n1z")
    action.drag_and_drop_by_offset(block, 500, 0)
    action.perform()
except:
    print("test missing")
    pass


driver.implicitly_wait(3)
while True:
    try:
        #sleep(2)
        totp = pyotp.TOTP(choose["Secret"])
        Auth = totp.now()
        driver.find_element_by_xpath("//input[@maxlength='6']").send_keys(Auth)
        #sleep(1)
        break
        #driver.find_element_by_xpath("//button[@type='submit']").click()
    except:
        print("can not find Secret")
        pass

    try:
        driver.find_element_by_id("nc_1_refresh1").click()
        action = ActionChains(driver)
        block = driver.find_element_by_id("nc_1_n1z")
        action.drag_and_drop_by_offset(block, 500, 0)
        action.perform()
    except:
        print("can not find refresh")
        pass

    try:
        driver.find_element_by_id("nc_2_refresh1").click()
        action = ActionChains(driver)
        block = driver.find_element_by_id("nc_1_n1z")
        action.drag_and_drop_by_offset(block, 500, 0)
        action.perform()
    except:
        print("can not find refresh")
        pass       

    



