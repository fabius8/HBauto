# -*- encoding=utf8 -*-
__author__ = "fabiu"

from airtest.core.api import *
import pyotp
import json
import os
import sys
from datetime import datetime
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

pointjson = json.load(open('point_hb.json'))
secret = ""
for item in pointjson:
    if item["Username"] == "gaodapigu@outlook.com":
        secret = item["Secret"]

auto_setup(__file__, ["android://127.0.0.1:5037/127.0.0.1:62038"])
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

if __name__ == "__main__":
    rowstart = 1
    rowend = 100
    for item in pointjson:
        if item["RowIndex"] < rowstart or item["RowIndex"] > rowend:
            print(item["RowIndex"], "skip")
            continue
        print(item)
        if "Point" not in item:
            print("miss point")
        elif 6 < (float(item["Point"])):
            print(item["Issuer"], " enough point skip!")
            continue
            
        poco("pro.huobi:id/id_points_transfer_uid").set_text(item["UID"])
        poco("pro.huobi:id/id_points_transfer_username").set_text(item["Username"])
        poco("pro.huobi:id/id_points_transfer_count").set_text("10")
        poco("pro.huobi:id/id_points_transfer_total_price").set_text("0.01")
        sleep(3.0)
        poco("pro.huobi:id/id_points_transfer_bottom_btn").click()
        poco("pro.huobi:id/dialog_confirm_btn").click()
        
        totp = pyotp.TOTP(secret)
        Auth = totp.now()
        poco("pro.huobi:id/et_ga_input").wait(timeout=5).set_text(Auth)
        sleep(1.0)
        poco("pro.huobi:id/btn_action").wait(timeout=5).click()
        poco("pro.huobi:id/iv_back").wait(timeout=5).click()
        poco(text="￼￼Transfer").wait(timeout=5).click()

        print(item["Issuer"], " get 10 point", )
        