#  -*- coding: utf-8 -*-

from datetime import datetime
import logging
import os

from selenium import webdriver

def main():
    # ログの設定
    dtNow = datetime.now()
    logFolder = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "log")
    logFile = os.path.join(logFolder,
                           dtNow.strftime("%y-%m-%d_%H-%M-%S") + ".log")
    if(not os.path.isdir(logFolder)):
        os.mkdir(logFolder)
        logging.info("logフォルダーを初期化")
    logging.basicConfig(filename=logFile,
                        level=logging.INFO,
                        format="%(asctime)s:%(funcName)s:%(message)s")
    logger = logging.getLogger("__name__")
    logging.info("実行開始")

    # 変数設定
    driverPath = os.path.join(os.path.dirname(__file__), "chromedriver.exe")
    tmpFolder = os.path.join(os.path.dirname(__file__), "tmp")
    userDataFolder = os.path.join(tmpFolder, "UserData")
    url = "https://accounts.google.com/signin/v2/identifier?hl=ja"
    if(not os.path.isdir(tmpFolder)):
        os.mkdir(tmpFolder)
        logging.info("tmpフォルダーを初期化")
    if(not os.path.isdir(userDataFolder)):
        os.mkdir(userDataFolder)
        logging.info("UserDataフォルダーを初期化")

    # Seleniumの設定
    logging.info("ブラウザの起動中...")
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=" + userDataFolder)
    driver = webdriver.Chrome(executable_path=driverPath, options=options)
    driver.implicitly_wait(30)
    logging.info(f"Chrome バージョン : {driver.capabilities['browserVersion']}")
    logging.info(f"Driver バージョン : {driver.capabilities['chrome']['chromedriverVersion']}")

    # スクレイピング開始
    driver.get(url)
    input("起動したブラウザを操作してGoogleにログインしてください。\n"+\
          "認証に成功したらEnterキーを入力して下さい。")
    driver.quit()
    logging.info("実行終了")

if(__name__ == "__main__"):
    main()