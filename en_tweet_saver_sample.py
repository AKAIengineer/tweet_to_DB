# Streamを利用して指定ユーザーのツイートをDBに保存
# 参考ページ↓

# TwitterAPI v2のStreamでTwitter自動リプライするよ
# https://zenn.dev/ryo427/articles/aeb7aaf22aa8f9

# 【Python×Twitter】検索ツイートのデータ取得・分析｜APIとtweepy活用による自動運用アプリ開発支援
# https://di-acc2.com/system/rpa/9690/#index_id6

# tweepyドキュメンテーション
# https://docs.tweepy.org/en/v4.10.1/index.html

# Twitter APIドキュメンテーション
# https://developer.twitter.com/en/docs/twitter-api

# requests - ChunkedEncodingError with requests.get, but not when using Postman
# https://stackoverflow.com/questions/70189517/requests-chunkedencodingerror-with-requests-get-but-not-when-using-postman

# Error decoding chunked response in _update_chunk_length: ValueError: invalid literal for int() with base 16: b'HTT...
# https://github.com/psf/requests/issues/4248

# 【PyMySQL】PythonでMySQL（MariaDB）に接続する
# https://self-development.info/%E3%80%90pymysql%E3%80%91python%E3%81%A7mysql%EF%BC%88mariadb%EF%BC%89%E3%81%AB%E6%8E%A5%E7%B6%9A%E3%81%99%E3%82%8B/

# MySQLのテーブル作成（CREATE TABLE）のサンプル
# https://yk5656.hatenadiary.org/entry/20141207/1426177469

# python で deepL API を使ってみる
# https://qiita.com/Negelon/items/ad0e47d15372e0d82ca9

import json
import os
import time
import traceback

import pymysql.cursors
import requests
import tweepy
from dotenv import load_dotenv

import translate

load_dotenv()

consumer_key = os.getenv("TWITTER_API_KEY")
consumer_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
host = os.getenv("HOST")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
db = os.getenv("DB")


def connect(host, user, password, db):
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        db=db,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return connection


def insert(tweet_id, user_id, username, text, text_ja, url):
    connection = connect(host, user, password, db)
    with connection.cursor() as cursor:
        # Create a new record
        sql = """
            INSERT INTO `tweet` (
                `tweet_id`, `user_id`, `username`, `text`, `text_ja`, `url`
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(sql, (tweet_id, user_id, username, text, text_ja, url))
    connection.commit()
    connection.close()


def ClientInfo():
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )
    return client


def GetTweet(tweet_id):
    GetTwt = ClientInfo().get_tweet(
        id=int(tweet_id), expansions=["author_id"], user_fields=["username"]
    )

    twt_result = {}
    twt_result["tweet_id"] = tweet_id
    twt_result["user_id"] = GetTwt.includes["users"][0].id
    twt_result["username"] = GetTwt.includes["users"][0].username
    twt_result["text"] = str(GetTwt.data)
    twt_result["url"] = (
        "https://twitter.com/"
        + GetTwt.includes["users"][0].username
        + "/status/"
        + str(tweet_id)
    )

    return twt_result


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )


def set_rules(delete):
    rules = [
        {"value": "from:**********"},
        {"value": "from:**********"},
    ]
    payload = {"add": rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )


def get_stream(headers):
    run = 1
    while run:
        try:
            with requests.get(
                "https://api.twitter.com/2/tweets/search/stream",
                auth=bearer_oauth,
                stream=True,
            ) as response:
                print(response.status_code)
                if response.status_code != 200:
                    raise Exception(
                        "Cannot get stream (HTTP {}): {}".format(
                            response.status_code, response.text
                        )
                    )
                for response_line in response.iter_lines(chunk_size=10240):
                    if response_line:
                        json_response = json.loads(response_line)

                        twt_result = GetTweet(json_response["data"]["id"])
                        tweet_id = twt_result["tweet_id"]
                        user_id = twt_result["user_id"]
                        username = twt_result["username"]
                        text = twt_result["text"]
                        url = twt_result["url"]

                        text_ja = translate.translate(text)

                        print("username: " + username)
                        print(text)
                        print("url: " + url)
                        print("=====================")
                        try:
                            with open("output.txt", "a") as f:
                                f.write(username + "\n")
                                f.write(text + "\n")
                                f.write(text_ja + "\n")
                                f.write("=================" + "\n\n")
                        except Exception:
                            print("txtに書き込みエラーだよ")
                        try:
                            insert(tweet_id, user_id, username, text, text_ja, url)
                        except Exception:
                            print("DBに挿入エラーだよ")
        except ChunkedEncodingError as e:
            print(traceback.format_exc())
            print(f"Invalid chunk encoding {str(e)}")
            time.sleep(6)
            continue
        except ConnectionError:
            print(traceback.format_exc())
            run += 1
            if run < 10:
                time.sleep(6)
                print("再接続します", run + "回目")
                continue
            else:
                run = 0
        except Exception:
            # some other error occurred.. stop the loop
            print(Exception)
            print(traceback.format_exc())
            run = 0


class ChunkedEncodingError(Exception):
    pass


def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    get_stream(set)


if __name__ == "__main__":
    while True:
        try:
            main()
        except requests.exceptions.ChunkedEncodingError:
            print("restarting")
