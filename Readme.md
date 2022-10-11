# 概要
## 背景
twitterの海外ユーザの英語のツイートを、日本語に自動翻訳して自動ツイートするボットを作りたかった。
まずはtwitter APIを使って指定したユーザのツイートを随時DBに保存していく工程を作成した。
## 概要
twitter APIを利用して、指定したユーザのツイートをstream状態（ポートを開いて常にlistenしている状態）で取得し、DBに保存する。
## 環境
tweepy==4.10.1 (tweepy: twitter APIを使いやすくするpythonライブラリ)
python-dotenv (.envを利用するためのライブラリ)
PyMySQL (pythonでmysqlに接続するためのライブラリ)

dockerを使用している。dockerの構成はdocker-compose.yml参照
# 実行手順
1. twitterAPIのアカウント登録(https://developer.twitter.com/en/docs/twitter-api)

    [Twitter APIで遊んでみた ~1. 各種キーの申請と取得~](https://tech-lab.sios.jp/archives/21238)←ここらへの記事を参考に登録してください。

    私はElevatedを申請しましたが、たぶんEssentialだけでも大丈夫です。

1. apt update, apt upgradeの実行
1. このgitをclone
1. docker起動
    ```
    $ sudo service docker start
    ```
1. APIキーや指定ユーザなどの変数を記入
- .envの各キー
- docker-compose.yml内のDB情報
- tweepy_streaming.py内の指定ユーザ
1. docker-composeビルド
    ```
    $ docker-compose up -d --build
    ```
1. mariadbのコンテナに入りtweetテーブル作成
    ```
    $ docker exec -it mysqlのコンテナID /bin/bash
    # mysql -uユーザ名 -pパスワード
    # use DB名
    # create table tweet (
      'tweet_id' bigint, 'user_id' bigint, 'username' text, 'text' text, 'url' text
    )
    ```
1. 実行
    ```
    $ docker-compose run python3 python tweepy_streaming.py
    ```
    実行したままサーバーをログアウトするばあいnohupを使う
    ```
    $ nohup docker-compose run python3 python tweepy_streaming.py &
    ```