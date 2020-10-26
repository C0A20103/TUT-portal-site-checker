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

def main():
    # ログの設定
    logFolder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
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
        raise Exception("指定されたディレクトリにChromeDriverが存在しません。")
    tmpFolder = os.path.join(os.path.dirname(__file__), "tmp")
    jsonFile = "GetData.json"
    jsonFolder = os.path.join(tmpFolder, jsonFile)
    userDataFolder = os.path.join(tmpFolder, "UserData")
    url = inifile.get("PORTAL_SITE_URL", "URL")
    if(not os.path.isdir(tmpFolder)): # jsonやUserDataを格納するtmpフォルダーの作製
        os.mkdir(tmpFolder)
        logger.info("tmpフォルダーを初期化")

    # Seleniumの設定
    logger.info("スクレイピング開始")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--user-data-dir=" + userDataFolder)
    driver = webdriver.Chrome(executable_path=driverPath, options=options)
    driver.implicitly_wait(30)

    # スクレイピング開始
    driver.get(url)
    if("google" in driver.current_url):
        logger.warning("Googleへのログインをサーバーから求められました。")
        if("アカウントの選択" in driver.page_source):
            actions = ActionChains(driver)
            actions.move_by_offset(400, 165)
            actions.click()
            actions.perform()
            time.sleep(3)
            logger.info("アカウントを選択...")

            loginPw = inifile.get("GOOGLE_ACCOUNT", "PASSWORD")
            pwInput = driver.switch_to.active_element
            pwInput.send_keys(loginPw)
            pwInput.send_keys(Keys.ENTER)
            time.sleep(3)
            logger.info("パスワードを入力...")

            if("google" in driver.current_url):
                driver.quit()
                raise Exception("ログインに失敗しました。login.pyから再ログインしてください。")
        else:
            driver.quit()
            raise Exception("ログインされていません。login.pyからログインしてください。")
        logger.info("認証成功")
        driver.get(url)
    htmlData = driver.page_source
    driver.quit()
    logger.info("HTMLデータの取得に成功しました")

    # HTMLをパース
    xml = lxml.html.fromstring(htmlData)
    getData = [xml.xpath(f"//*[@id='tab1']/li[{i}]/a/p")[0].text_content() for i in range(1, 11)]

    # 新着タイトルを抽出
    try:
        with open(jsonFolder, mode="r", encoding="utf-8") as f:
            oldData = json.loads(f.read())
            logger.info("jsonファイルの読み込みに成功しました")
    except:
        oldData = []
        logger.warning("jsonファイルの読み込みに失敗しました")
    newData = [i for i in getData if(not i in oldData)]

    # 新着タイトルをLINEで通知
    reply = ""
    for i in newData:
        reply += f"・{i}\n\n"
    if(newData):
        lineMSG(inifile.get("LINE_ACCESS_TOKEN", "KEY"),
                f"\nポータルサイトが{len(newData)}件更新されました。\n\n"+\
                reply+\
                f"ポータルサイトはこちら\n{url}")
        logger.info("LINEへ送信完了")
    else:
        logger.info("更新されていなかったため、LINEへ通知しませんでした。")

    # 正規表現で抽出した情報を全てjsonファイルとして保存
    with codecs.open(jsonFolder, "w", "utf-8") as f:
        json.dump(getData, f, ensure_ascii = False, indent=4)
    logger.info("jsonファイルの保存完了")

    logger.info("実行終了")

if(__name__ == "__main__"):
    main()