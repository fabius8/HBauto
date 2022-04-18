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

def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            print("Port is open")
            return True
        else:
            print("Port is not open")
            return False

point_hb_json_file = "point_hb.json"
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
        if poco("pro.huobi:id/tv_account_uid").wait(timeout=2).exists():
            print("Already login")
            return
        elif poco(textMatches=".*Sign Up").wait(timeout=10).exists():
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
                    poco("pro.huobi:id/et_ga_input").wait(timeout=10).set_text(Auth)
                    poco("pro.huobi:id/btn_action").click()

    
def getPoint():    
    Point = poco("pro.huobi:id/points_notice_box_text_number").wait(timeout=5).get_text()
    UID = poco("pro.huobi:id/tv_account_uid").get_text()
    for item in secretjson:
        if item["UID"] in UID:
            item["Point"] = Point
            print(item["Issuer"], UID, Point)
    return Point
    
def switchAccount():
    poco("pro.huobi:id/main_account_tab_checkbox").wait(timeout=10).click()
    poco("pro.huobi:id/v_setting_count_dot").click()
    poco("pro.huobi:id/id_common_list_change_btn").click()
    # move down to choose last account
    poco("pro.huobi:id/account_rv").swipe([-0.1101, -0.38])
    poco("pro.huobi:id/account_rv").child("pro.huobi:id/account_root_view")[-1].wait(timeout=10).click()
    if not poco("pro.huobi:id/login_account_edit").exists():
        print("Seems all login success")
        poco("pro.huobi:id/iv_back").click()
        sleep(1.0)
        poco("pro.huobi:id/iv_back").click()
        return True
    else:
        return False


if __name__ == "__main__":
    hbstart = "HB_01"
    hbend = "HB_12"
    for i in adbportsjson:
        index = i["Index"]
        name = i["Name"]
        if name == hbstart or hbstart == "":
            print("start from ", hbstart)
            hbstart=""
        elif name == hbend:
            break
        else:
            print(i["Name"], "skip")
            continue
        Adbport = i["AdbPort"]
        startVirtual(index, Adbport)
        print("adbport:", Adbport)
        auto_setup(__file__, devices=getAdbPortURI(Adbport))
        poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
        
        start_app(package="com.v2ray.ang")
        poco("com.v2ray.ang:id/fab").wait(timeout=10).click()
        keyevent("HOME")
        start_app(package="pro.huobi")
        sleep(3.0)

        count = 0
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        while True:
            sleep(3.0)
            login()
            getPoint()
            switchAccount()
            count += 1
            if count >= 10:
                break
            
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        with open(point_hb_json_file, "w", encoding='utf-8') as f:
            json.dump(secretjson, f, indent=4, ensure_ascii=False)
        stopVirtual(index, Adbport)
        print("end")

