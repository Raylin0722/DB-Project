import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

# 載入環境變數
load_dotenv()

# 首先檢查是否存在 MYSQL_URL 環境變數
# 如果存在，則解析 URL 並提取資料庫連線資訊
# 依次檢查標準變數名稱和 Railway 特定的變數名稱
MYSQL_USER = os.getenv('MYSQL_USER') or os.getenv('MYSQLUSER') or 'root'
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD') or os.getenv('MYSQLPASSWORD') or os.getenv('MYSQL_ROOT_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST') or os.getenv('MYSQLHOST') or 'localhost'
MYSQL_PORT = int(os.getenv('MYSQL_PORT') or os.getenv('MYSQLPORT') or '3306')
MYSQL_DB = os.getenv('MYSQL_DATABASE') or os.getenv('MYSQLDATABASE') or 'railway'

# 建立 MySQL 連線池
pool_config = {
    "host": MYSQL_HOST,
    "user": MYSQL_USER,
    "password": MYSQL_PASSWORD,
    "database": MYSQL_DB,
    "port": MYSQL_PORT,
    "pool_name": "mypool",
    "pool_size": 20  # 設定連線池大小
}

try:
    connection_pool = MySQLConnectionPool(**pool_config)
    print(f"成功連接到 MySQL 資料庫：{MYSQL_DB}@{MYSQL_HOST}:{MYSQL_PORT}")
except mysql.connector.Error as err:
    print(f"連接資料庫失敗：{err}")
    # 可以加入重試邏輯或者其他錯誤處理機制

# 測試連接的函數
def test_connection():
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        cursor.close()
        connection.close()
        return f"成功連接到 MySQL 資料庫！版本: {version[0]}"
    except mysql.connector.Error as err:
        return f"連接失敗: {err}"

# 如果直接執行此檔案，則測試連接
if __name__ == "__main__":
    print(test_connection())