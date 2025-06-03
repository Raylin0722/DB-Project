import flask
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from dotenv import load_dotenv
import os
import json  # 用於 JSON 格式化

# 載入環境變數
load_dotenv()

# 從環境變數中取得 MySQL 連接資訊
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = os.getenv('SERVER_PORT')

# 建立 MySQL 連線池
pool_config = {
    "host": MYSQL_HOST,
    "user": MYSQL_USER,
    "password": MYSQL_PASSWORD,
    "database": "team1",
    "pool_name": "mypool",
    "pool_size": 20  # 設定連線池大小
}
connection_pool = MySQLConnectionPool(**pool_config)

# 建立 Flask 應用程式
app = flask.Flask(__name__)

def query_result_to_json(result):
    """將查詢結果轉換為 JSON 格式"""
    return json.dumps([{"database_name": row[0]} for row in result])

@app.route('/')
def index():
    return "Hello, World! This is the Flask server."

@app.route('/testSQL')
def home():
    # 從連線池中取得連線
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES;")
        tables = cursor.fetchall()
        cursor.close()
        connection.close()

        # 將查詢結果轉換為 JSON 格式並返回
        return query_result_to_json(tables)
    except mysql.connector.Error as err:
        return json.dumps({"error": str(err)})

if __name__ == '__main__':
    app.run(host=SERVER_IP, port=SERVER_PORT, debug=True)
