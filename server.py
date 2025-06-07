import flask
import os
from dotenv import load_dotenv
from auth.routes import auth_bp
from post.post import post_bp
from auth.lost_routes import lost_bp
from flask_mail import Mail
from flask_mail import Message
from flask import render_template
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta  



# 初始化
mail = Mail()
load_dotenv()

SERVER_IP = os.getenv('SERVER_IP')
SERVER_PORT = os.getenv('SERVER_PORT')

# 建立 Flask 應用程式
app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') 
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('師大校園失物招領系統',os.getenv('MAIL_DEFAULT_SENDER'))
mail.init_app(app)

# 建立 token serializer 並註冊給 current_app 使用
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
app.mail = mail
app.token_serializer = s

# 設定 Session 有效時間
app.permanent_session_lifetime = timedelta(minutes=30)

# 註冊 blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(lost_bp)
app.register_blueprint(post_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host=SERVER_IP, port=SERVER_PORT, debug=True)
