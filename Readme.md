# 概要
## 背景
twitterの海外ユーザの英語のツイートを、日本語に自動翻訳して自動ツイートするボットを作りたかった。
まずはtwitter APIを使って指定したユーザのツイートと、それをdeeplAPIで翻訳したtextを、随時DBに保存していく工程を作成した。
## 概要
twitter APIを利用して、指定したユーザのツイートをstream状態（ポートを開いて常にlistenしている状態）で取得し、DBに保存する。

deepl APIを利用して、英語のtextを自動で日本語textに変換し、それもDBに保存する。
## 環境
tweepy==4.10.1 (tweepy: twitter APIを使いやすくするpythonライブラリ)

python-dotenv (.envを利用するためのライブラリ)

PyMySQL (pythonでmysqlに接続するためのライブラリ)

dockerを使用している。dockerの構成はdocker-compose.yml参照
# 実行手順
1. twitterAPIのアカウント登録(https://developer.twitter.com/en/docs/twitter-api)

    [Twitter APIで遊んでみた ~1. 各種キーの申請と取得~](https://tech-lab.sios.jp/archives/21238)←ここらへの記事を参考に登録してください。

    私はElevatedを申請しましたが、たぶんEssentialだけでも大丈夫です。
1. deeplAPI登録

    こちらはメールアドレスや住所などのプロフィールを登録するだけ
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
      'tweet_id' bigint, 'user_id' bigint, 'username' text, 'text' text, 'text_ja' text, 'url' text
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
# 参考文献
[TwitterAPI v2のStreamでTwitter自動リプライするよ](https://zenn.dev/ryo427/articles/aeb7aaf22aa8f9)

[Python×Twitter】検索ツイートのデータ取得・分析｜APIとtweepy活用による自動運用アプリ開発支援](https://di-acc2.com/system/rpa/9690/#index_id6)

[tweepyドキュメンテーション](https://docs.tweepy.org/en/v4.10.1/index.html)

[Twitter APIドキュメンテーション](https://developer.twitter.com/en/docs/twitter-api)

[requests - ChunkedEncodingError with requests.get, but not when using Postman](https://stackoverflow.com/questions/70189517/requests-chunkedencodingerror-with-requests-get-but-not-when-using-postman)

[Error decoding chunked response in _update_chunk_length: ValueError: invalid literal for int() with base 16: b'HTT...](https://github.com/psf/requests/issues/4248)

[【PyMySQL】PythonでMySQL（MariaDB）に接続する](https://self-development.info/E3%80%90pymysql%E3%80%91python%E3%81%A7mysql%EF%BC%88mariadb%EF%BC%89%E3%81%AB%E6%8E%A5%E7%B6%9A%E3%81%99%E3%82%8B/)

[MySQLのテーブル作成（CREATE TABLE）のサンプル](https://yk5656.hatenadiary.org/entry/20141207/1426177469)

[python で deepL API を使ってみる](https://qiita.com/Negelon/items/ad0e47d15372e0d82ca9)