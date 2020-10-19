#  -*- coding: utf-8 -*-

import codecs
import configparser
from datetime import datetime
import json
import logging
import os
import pathlib
import requests
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import lxml.html

import login

def setupLogger(logLevel=logging.INFO): #ログ出力初期化関数
    logger = logging.getLogger(__name__)
    logger.setLevel(logLevel)

    sh = logging.StreamHandler()
    sh.setLevel(logLevel)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    dtNow = datetime.now()
    logFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "log",
                           dtNow.strftime("%y-%m-%d_%H-%M-%S") + ".log")
    fh = logging.FileHandler(logFile)
    fh.setLevel(logLevel)
    fhFormatter = logging.Formatter("%(asctime)s - %(filename)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s")
    fh.setFormatter(fhFormatter)
    logger.addHandler(fh)
    return logger

def lineMSG(message): #LINE通知用関数
    url = "https://notify-api.line.me/api/notify"
    accessToken = os.environ["LINE_ACCESS_TOKEN"]
    headers = {"Authorization": f"Bearer {accessToken}"}
    payload = {"message": message}
    r = requests.post(url, headers=headers, params=payload)
    logging.info("LINEへ送信完了")

def main():
    # ログの設定
    logFolder = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "log")
    if(not os.path.isdir(logFolder)):
        os.mkdir(logFolder)
    logger = setupLogger()
    logger.info("実行開始")

    # 変数設定
    inifile = configparser.ConfigParser()
    inifile.read(os.path.join(os.path.dirname(__file__), "setting.ini"), encoding="utf-8")
    driverPath = pathlib.Path(inifile.get("CHROME_DRIVER_PATH", "PATH"))
    if(not driverPath.is_absolute()):
        driverPath = os.path.join(os.path.dirname(__file__), driverPath)
    driverPath = str(driverPath)
    if(not os.path.isfile(driverPath)):
        raise Exception("下記の場所にchromedriverが存在しません。\n"+\
                        f"{driverPath}")
    tmpFolder = os.path.join(os.path.dirname(__file__), "tmp")
    jsonFile = "GetData.json"
    jsonFolder = os.path.join(tmpFolder, jsonFile)
    userDataFolder = os.path.join(tmpFolder, "UserData")
    url = inifile.get("PORTAL_SITE_URL", "URL")
    if(not os.path.isdir(tmpFolder)): # jsonやUserDataを格納するtmpフォルダーの作製
        os.mkdir(tmpFolder)
        logger.info("tmpフォルダーを初期化")
    if(not os.path.isdir(userDataFolder)): # Chromeのキャッシュを格納するUserDataフォルダーの作製
        os.mkdir(userDataFolder)
        logger.info("UserDataフォルダーを初期化")

    # Seleniumの設定
    logger.info("スクレイピング開始")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--user-data-dir=" + userDataFolder)
    driver = webdriver.Chrome(executable_path=driverPath, options=options)
    driver.implicitly_wait(30)
    logger.info(f"Chrome バージョン : {driver.capabilities['browserVersion']}")
    logger.info(f"Driver バージョン : {driver.capabilities['chrome']['chromedriverVersion']}")

    # スクレイピング開始
    driver.get(url)
    logger.debug(f"↓下記のサイトに接続\n{driver.current_url}")
    if("google" in driver.current_url):
        # Googleにログイン情報を求められたら
        logger.warning("Googleへのログインをサーバーから求められました。")
        if("アカウントの選択" in driver.page_source):
            # アカウントの選択
            actions = ActionChains(driver)
            actions.move_by_offset(400, 165)
            actions.click()
            actions.perform()
            time.sleep(3)
            logger.info("アカウントを選択...")

            # パスワード入力
            loginPw = inifile.get("GOOGLE_ACCOUNT", "PASSWORD")
            pwInput = driver.switch_to.active_element
            pwInput.send_keys(loginPw)
            pwInput.send_keys(Keys.ENTER)
            time.sleep(3)
            logger.info("パスワードを入力...")

            # 認証に失敗したらエラーを投げる
            if("google" in driver.current_url):
                driver.quit()
                raise Exception("自動再ログインに失敗しました。手動で再ログインしてください。")
        else:
            # 認証に失敗したらエラーを投げる
            logger.warning("ログインされていません。手動でログインしてください。")
            driver.quit()
            login.main()
            logger.info("認証情報が変更されました。再起動してください。")
            exit()
        logger.info("認証成功")
        driver.get(url)
    htmlData = driver.page_source
    driver.quit()
    logger.info("HTMLデータの取得に成功しました")

    # 取得したHTMLを解析して情報抽出
    xml = lxml.html.fromstring(htmlData)
    getData = []
    for i in range(1, 11):
        dates = xml.xpath(f'//*[@id="tab1"]/li[{i}]/datetime')
        cats = xml.xpath(f'//*[@id="tab1"]/li[{i}]/span')
        for j in range(len(cats)):
            cats[j] = cats[j].text
        titles = xml.xpath(f'//*[@id="tab1"]/li[{i}]')
        title = titles[0].text_content().split("\n")[2].replace("\t", "")
        getData.append({"date" : dates[0].text, "category" : cats, "title" : title})

    # 新着用件のみを抽出
    try:
        with open(jsonFolder, mode="r", encoding="UTF-8") as f:
            fileRead = f.read()
        print(type(fileRead))
        oldData = json.loads(fileRead)
        oldData = oldData["data"]
        logger.info("jsonファイルの読み込みに成功しました")
    except:
        logger.warning("jsonファイルの読み込みに失敗")
        oldData = [{"date" : "", "category" : [], "title" : ""}]
    newData = []
    for i in getData:
        if(i["title"] != oldData[0]["title"]):
            newData.append(i)
        else:
            break

    # 抽出した新着用件のみをLINEで通知
    reply = ""
    logger.debug(f"newData: len{len(newData)} {list(newData)}")
    for i in range(3):
        if (len(newData) <= i or len(newData) == 0):
            break
        else:
            reply = reply + newData[i]["title"] + "\n\n"
            logger.debug("reply:",reply)
    if(0 < len(newData)):
        lineMSG(inifile.get("LINE_ACCESS_TOKEN", "KEY"),
                f"\nポータルサイトが{len(newData)}件更新されました。\n\n"+\
                reply+\
                f"ポータルサイトはこちら\n{url}")
    else:
        logger.info("更新されていなかったため、LINEへ通知しませんでした。")

    # 正規表現で抽出した情報を全てjsonファイルに保存
    dtNow = datetime.now()
    writeData = {"data":getData, "updated_at":dtNow.strftime("%Y/%m/%d %H:%M:%S"), "url":url}
    with codecs.open(jsonFolder, "w", "utf-8") as f:
        json.dump(writeData, f, ensure_ascii = False, indent=4)
    logger.info("jsonファイルの保存完了")

    logger.info("実行終了")

if(__name__ == "__main__"):
    main()