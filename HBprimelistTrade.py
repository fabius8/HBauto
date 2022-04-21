# -*- encoding=utf8 -*-
__author__ = "fabiu"

from airtest.core.api import *
import pyotp
import json
import os
import sys
from datetime import datetime
from poco.drivers.android.uiautomation import AndroidUiautomationPoco

import socket
from contextlib import closing
#import logging
#logger = logging.getLogger("airtest")
#logger.setLevel(logging.ERROR)

def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            print("Port is open")
            return True
        else:
            print("Port is not open")
            return False

secretjson = json.load(open('point_hb.json'))
adbportsjson = json.load(open('adbports.json'))

        
def startVirtual(index, Adbport):
    yeshenDIR = "E:\\夜神数据\\Nox\\bin"
    yeshenEXE = "NoxConsole.exe"
    yeshenStartCommand = "start /d " + yeshenDIR + " " + yeshenEXE + " launch -index:" + str(index)
    print(yeshenStartCommand)
    os.system(yeshenStartCommand)
    while True:
        sleep(5)
        if check_socket('localhost', Adbport):
            sleep(10)
            break

def stopVirtual(index, Adbport):
    yeshenDIR = "E:\\夜神数据\\Nox\\bin"
    yeshenEXE = "NoxConsole.exe"
    yeshenStopCommand = "start /d " + yeshenDIR + " " + yeshenEXE + " quit -index:" + str(index)
    print(yeshenStopCommand)
    os.system(yeshenStopCommand)
            
def getAdbPortURI(AdbPort):
    return ["android://127.0.0.1:5037/127.0.0.1:" + str(Adbport)]

    
def login():
    if poco("pro.huobi:id/main_account_tab_checkbox").exists():
        poco("pro.huobi:id/main_account_tab_checkbox").click()
        sleep(2)
        if poco(textMatches="UID.*").wait(timeout=2).exists():
            print("Already login")
            return
    if poco(textMatches=".*Sign Up").wait(timeout=10).exists():
        print("Login again")
        poco("pro.huobi:id/tv_account_name").click()
        
    if poco("pro.huobi:id/login_account_edit").wait(timeout=10).exists():
        Email = poco("pro.huobi:id/login_account_edit").get_text()
        Auth = ""
        for i in secretjson:
            if Email in i["Username"]:
                print(i["Issuer"], i["Password"])
                poco("pro.huobi:id/login_psw_edit").set_text(i["Password"])
                poco("pro.huobi:id/text_view_widget_status_button_text").click()
                
                totp = pyotp.TOTP(i["Secret"])
                Auth = totp.now()
                
                if poco("pro.huobi:id/et_ga_input").wait(timeout=5).exists():
                    poco("pro.huobi:id/et_ga_input").set_text(Auth)
                    poco("pro.huobi:id/btn_action").click()
                elif poco("nc_1_n1z").wait(timeout=10).exists():
                    poco("nc_1_n1z").swipe([1, 0.015])
                    if poco(textMatches=".*Please refresh and.*").wait(timeout=2).exists():
                        poco(textMatches=".*Please refresh and.*").click()
                        poco("nc_1_n1z").swipe([1, 0.015])
                        poco("pro.huobi:id/et_ga_input").wait(timeout=10).set_text(Auth)
                        poco("pro.huobi:id/btn_action").click()

    
def primlistTrade():
    tradeVolume = 2000.0
    poco("pro.huobi:id/main_index_cb").wait(timeout=10).click()
    poco(text="Primelist").wait(timeout=10).click()
    sleep(10)
    needVolume = 0
    while True:
        if poco(text="/500 USDT").wait(timeout=10).exists(): 
            strVolume = poco(text="/500 USDT").sibling(name="android.widget.TextView").get_text()
            doVolume = float(strVolume.replace(',', ''))
            needVolume = tradeVolume - doVolume * 4
            print("Need Volume:", needVolume)
            if needVolume > 0:
                break
            else:
                keyevent("BACK")
                return needVolume
        else:
            keyevent("BACK")
            poco(text="Primelist").wait(timeout=10).click()
            sleep(10)

    if needVolume > 0:
        times = needVolume / 100 + 1
        poco(textMatches="Trade Now").click()
        poco("pro.huobi:id/trade_type_tv").click()
        poco(textMatches="Market Order").click()
        for i in range(int(times)):
            print("BUY")
            while True:
                poco(text="Buy").wait(timeout=10).click()
                sleep(1)
                text = poco("pro.huobi:id/tv_available_fund_value").wait(timeout=10).get_text()
                if text == "--":
                    sleep(1)
                    continue
                if float(text) < 50.1:
                    break
                poco("pro.huobi:id/input_amount_et").set_text("50.1")
                poco(text="Buy BTC").wait(timeout=10).click()
                break
            print("SELL")
            while True:
                poco(text="Sell").wait(timeout=10).click()
                sleep(1)
                text = poco("pro.huobi:id/tv_available_fund_value").get_text()
                if text == "--":
                    sleep(1)
                    continue
                poco("pro.huobi:id/leverage_100").click()
                poco(text="Sell BTC").wait(timeout=10).click()
                break
    return needVolume
                
def switchAccount():
    poco("pro.huobi:id/main_account_tab_checkbox").wait(timeout=10).click()
    poco("pro.huobi:id/v_setting_count_dot").click()
    poco("pro.huobi:id/id_common_list_change_btn").click()
    # move down to choose last account
    poco("pro.huobi:id/account_rv").swipe([-0.1101, -0.38])
    poco("pro.huobi:id/account_rv").child("pro.huobi:id/account_root_view")[-1].wait(timeout=10).click()
    if not poco("pro.huobi:id/login_account_edit").exists():
        print("Seems all login success")
        keyevent("BACK")
        sleep(1.0)
        keyevent("BACK")
        return True
    else:
        return False


if __name__ == "__main__":
    hbstart = "HB_08"
    hbend = "HB_24"
    end = 0
    for i in adbportsjson:
        index = i["Index"]
        name = i["Name"]
        if name == hbend:
            if end == 0:
                end = end + 1
            else:
                break
        elif name == hbstart or hbstart == "":
            print("start from ", hbstart)
            hbstart=""
        else:
            print(i["Name"], "skip")
            continue
        Adbport = i["AdbPort"]
        startVirtual(index, Adbport)
        print("adbport:", Adbport, i["Name"])
        auto_setup(__file__, devices=getAdbPortURI(Adbport))
        poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
        start_app(package="com.v2ray.ang")
        poco("com.v2ray.ang:id/fab").wait(timeout=10).click()
        keyevent("HOME")
        start_app(package="pro.huobi")
        sleep(3.0)

        count = 1
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        with open(str(i["Name"]) + ".txt", "w") as file:
            text = "\n"
            file.write(text)
        while True:
            print(count)
            sleep(3.0)
            login()
            needVol = primlistTrade()
            with open(str(i["Name"]) + ".txt", "a") as file:
                text = str(count) + " " + str(needVol) + "\n"
                file.write(text)
            switchAccount()
            count += 1
            if count > 10:
                break
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        stopVirtual(index, Adbport)
        print("end")

