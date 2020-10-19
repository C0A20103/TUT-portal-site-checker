# 名前

TUT portal site checker

# 概要

実行された時、TUTのポータルサイトが更新されていたらLINEで通知するプログラム。

# 概要欄なんざいらねぇ！

自動化がお好き？　けっこう。ではますます好きになりますよ。さぁさぁ、どうぞ。自作の自動化ツールです。  
…便利でしょう？　んああぁ、おっしゃらないで。  
実行環境がローカル。でもレンタルサーバーなんて見かけだけで、知識は必要だし、金がかかるわ、すぐ仕様変更するわ、ろくなことはない。  
拡張性もたっぷりありますよ。どんなパイソニアの方でも大丈夫。どうぞ改造してみてください。  
…いい発想でしょう？　怠惰の証だ、根性が違いますよ  
何です？  
わーっ、何を！　わぁ、待って！　サーバーでループさせちゃ駄目ですよ！　待って！　止まれ！　うわぁーっ！！  

※ループ実行や頻繁に実行させることは接続先のサーバーに負荷をかけるのでやめてください。

# 必要なソフトウェアとライブラリ

必要なソフトウェア

* Python 3.7.7
* Chrome 86.0.4240.75
* ChromeDriver 86.0.4240.22

必要なPythonライブラリ

* lxml 4.6.1
* requests 2.24.0
* selenium 3.141.0
* urllib3 1.25.10

※いずれもバージョンを記載してありますが、基本的にどのバージョンでも動きます。ただし、Pythonは3.X系を使ってください。  
※Chromeは常に最新版に、ChromeDriverはChromeに対応するバージョンを選択してダウンロードしてください。

# ソフトウェアとライブラリのインストール

※PythonとChromeが既にインストールされている前提で説明を続けます。

## ChromeDriverのインストール方法

1. [ChromeDriverダウンロードページ](https://chromedriver.chromium.org/downloads)からインストールされているChromeのバージョンとOSに対応するものをダウンロードしてください。

2. ダウンロードしたzipファイルを展開し、中に入っている`chromedriver.exe`(macOSは`chromedriver`)を`main.py`が存在するフォルダへ移動してください。

3. 1~2の操作をすると以下のようなフォルダ構造になります。(Windowsの場合)

```directory
├── chromedriver.exe
├── login.py
├── main.py
├── README.md
├── requirements.txt
└── setting.ini
```

※macOSの方は`setting.ini`の`[CHROME_DRIVER_PATH][PATH]`の部分を`chromedriver.exe`から`chromedriver`へ変更してください。

※ChromeDriverが既に別の場所に配置されている場合は、その絶対パスを`setting.ini`の`[CHROME_DRIVER_PATH][PATH]`の部分に書き込むと読み込むことができます。

## Pythonライブラリのインストール方法

1. ライブラリをpipを使ってダウンロードします。

```bash
pip install lxml
```

```bash
pip install requests
```

```bash
pip install selenium
```

# 使い方

## 初期設定

1. `CromeDriver`がセットされていることを確認します。
2. [LINE Notify](https://notify-bot.line.me/ja/)からアクセストークンを発行してトークン(発行された40文字程度の文字列)を取得してください。
3. 取得したトークンを`setting.ini`の`[LINE_ACCESS_TOKEN][KEY]`の部分に入力して保存してください。
4. `setting.ini`の`[PORTAL_SITE_URL][URL]`の部分を任意のアドレスに。(デフォルトの状態だと応用生物学部)ここで設定した学部の情報がLINEで通知されます。
5. コマンドライン上で`login.py`を実行。表示されたChromeウィンドウから**TUTのポータルサイトにアクセスできる権限を持つGoogleアカウント**でログインしてください。
6. ログインが完了したらコマンドライン上でEnterキーを入力してください。入力されるとChromeウィンドウが自動的に閉じられます。

## 実行方法

1. 初期設定が完了していることを確認する。
2. `main.py`を実行する。

```cmd
python main.py
```

※毎回手動で起動させるのは手間がかかるので、WindowsのタスクスケジューラやMacのcronなどを用いて定期実行させると非常に便利です。

# 注意点

- **このプログラムを使用、複製、改造をはじめとする如何なる行為や、それによって生じた損害に対して開発者は一切の責任を負いかねます。**
- **ループ実行や頻繁に実行させることは接続先のサーバーに負荷をかけるのでやめてください。**
- このコードはローカル環境(お使いのPC上)で実行されることを考えて製作されています。
- プログラムを実行して生成される`tmpフォルダ`はユーザーのログイン情報などが書かれているので流出させないように注意してください。
- プログラムを実行して生成される`logフォルダ`にはログが出力されます。エラーが発生した場合の参考にしてください。
- 毎回手動で起動させるのは手間がかかるので、WindowsのタスクスケジューラやMacのcronなどを用いて定期実行させると非常に便利です。

# ライセンス
わかんない( ᐛ)  
秘密にするようなことが書かれていないので、部外者に渡しても特に問題ないのでは？