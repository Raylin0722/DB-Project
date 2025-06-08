from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message

match_bp = Blueprint('match', __name__)

@match_bp.route('/send-match-email', methods=['POST'])
def send_match_email():
    data = request.get_json()
    email = data['school_email']
    username = data['username']

    try:
        msg = Message('師大校園失物招領系統 配對成功通知', recipients=[email])
        msg.body = f'''您好 {username}:

您登記的物品已有初步配對結果，請盡快上系統網頁確認配對項目是否正確。

若配對正確，請依系統指示完成後續領取流程。

如有疑問，請聯繫系統管理員或客服信箱。

謝謝您使用本系統！

師大校園失物招領系統 敬上

（此信件由系統自動發出，請勿回覆本信件）'''

        current_app.mail.send(msg)
        return jsonify({"status": "success", "message": "✅ 配對成功通知信已寄出"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
