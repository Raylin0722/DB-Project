from flask import Blueprint, request, jsonify, current_app, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from db import connection_pool
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)
temp_users = {} 

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['school_email']

    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Users WHERE school_email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "此信箱已註冊，請直接登入"}), 400
        
        cursor.execute("""
            DELETE FROM TempUsers WHERE created_at < (UTC_TIMESTAMP() - INTERVAL 1 HOUR)
        """)
        
        # 檢查是否已經存在於 TempUsers 表中（尚未驗證）
        cursor.execute("SELECT * FROM TempUsers WHERE school_email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "⚠ 此信箱已送出驗證信，請先前往信箱完成驗證"}), 400

        # 儲存進 TempUsers
        hashed_pw = generate_password_hash(data['password'])
        cursor.execute("""
            INSERT INTO TempUsers (username, school_email, password_hash, department, phone)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['username'], email, hashed_pw, data['department'], data['phone']))
        conn.commit()

        # 發送驗證信
        s = current_app.token_serializer
        token = s.dumps(email, salt='email-confirm')
        confirm_link = url_for('auth.confirm_email', token=token, _external=True)

        msg = Message('師大校園失物招領系統 信箱驗證', recipients=[email])
        msg.body = f'您好:\n感謝您註冊師大校園失物招領系統，請點擊以下連結完成帳號驗證，為確保資料安全，此網址於1小時內有效\n\n{confirm_link}\n\n師大校園失物招領系統敬上\n\n信件由系統自動發出，請勿回覆本信件。'
        current_app.mail.send(msg)

        return jsonify({"status": "success", "message": "✅ 驗證信已寄出，請至信箱點擊連結完成註冊"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


@auth_bp.route('/verify')
def confirm_email():
    token = request.args.get('token')
    try:
        s = current_app.token_serializer
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except Exception as e:
        return f'驗證失敗或連結已過期', 400

    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()

        # 檢查正式帳號是否已存在
        cursor.execute("SELECT * FROM Users WHERE school_email = %s", (email,))
        if cursor.fetchone():
            return '該信箱已完成註冊', 400

        # 從 TempUsers 取出資料
        cursor.execute("SELECT * FROM TempUsers WHERE school_email = %s", (email,))
        temp_user = cursor.fetchone()
        if not temp_user:
            return '找不到驗證中的帳號', 400

        # 寫入正式 Users
        cursor.execute("""
            INSERT INTO Users (username, school_email, password_hash, department, phone, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (temp_user[1], temp_user[2], temp_user[3], temp_user[4], temp_user[5], 'member'))

        # 刪除暫存
        cursor.execute("DELETE FROM TempUsers WHERE school_email = %s", (email,))
        conn.commit()

        return '✅ 註冊成功！您現在可以登入'

    except Exception as e:
        return f'資料庫錯誤：{str(e)}', 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['school_email']
        password = data['password']

        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Users WHERE school_email = %s", (email,))
        user = cursor.fetchone()

        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({"status": "error", "message": "信箱或密碼錯誤"}), 401

        print(f"收到登入請求：{{使用者: {email}}}")
        return jsonify({
            "status": "success",
            "message": "登入成功",
            "user": {
                "user_id": user['user_id'],
                "username": user['username'],
                "role": user['role']
            }
        })
    except Exception as e:
        print("登入錯誤:", str(e))  
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
        
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('school_email')

    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()

        # 取得 user_id
        cursor.execute("SELECT user_id FROM Users WHERE school_email = %s", (email,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"status": "error", "message": "查無此信箱"}), 404
        user_id = row[0]
        
        # 刪除1小時內未更改密碼，上次變更為3天前
        cursor.execute("""
            DELETE FROM PasswordResetRequests
            WHERE
                (used = 0 AND expiry < UTC_TIMESTAMP())
                OR
                (used = 1 AND created_at < (UTC_TIMESTAMP() - INTERVAL 3 DAY))
        """)
        
        # 三天內變更過密碼
        cursor.execute("""
            SELECT 1 FROM PasswordResetRequests
            WHERE user_id = %s AND used = 1 AND created_at > UTC_TIMESTAMP() - INTERVAL 3 DAY
        """, (user_id,))
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "⚠ 您已於三日內變更過密碼"
            }), 429

        # 檢查是否已有未使用、未過期的 token
        cursor.execute("""
            SELECT * FROM PasswordResetRequests
            WHERE user_id = %s AND used = 0 AND expiry > UTC_TIMESTAMP()
        """, (user_id,))
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "⚠ 您已申請過密碼重設，請至信箱查看或稍後再試"
            }), 429

        # 建立新 token 與過期時間
        s = current_app.token_serializer
        token = s.dumps(email, salt='password-reset')
        create_at=datetime.utcnow()
        expiry = datetime.utcnow() + timedelta(hours=1)

        # 寫入PasswordResetRequests
        cursor.execute("""
            INSERT INTO PasswordResetRequests (token, created_at,expiry, used, user_id)
            VALUES (%s,%s, %s, 0, %s)
        """, (token,create_at, expiry, user_id))
        conn.commit()

        # 發送密碼變更信件
        reset_link = url_for('auth.reset_password_page', token=token, _external=True)
        msg = Message('師大校園失物招領系統 密碼變更', recipients=[email])
        msg.body = f'您好:\n感謝您使用師大校園失物招領系統，請點擊以下連結完成密碼變更設定，為確保資料安全，此網址於1小時內有效\n\n{reset_link}\n\n師大校園失物招領系統敬上\n\n信件由系統自動發出，請勿回覆本信件。'
        current_app.mail.send(msg)

        return jsonify({"status": "success", "message": "✅ 重設密碼信已寄出，請至信箱查看"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

        
@auth_bp.route('/reset-password')
def reset_password_page():
    return render_template('reset_password.html')

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')

    try:
        s = current_app.token_serializer
        email = s.loads(token, salt='password-reset', max_age=3600)
    except Exception as e:
        return jsonify({"status": "error", "message": f"驗證失敗或連結已過期"}), 400

    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()

        # 取得 user_id
        cursor.execute("SELECT user_id FROM Users WHERE school_email = %s", (email,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"status": "error", "message": "使用者不存在"}), 404
        user_id = row[0]

        # 確認 token 是否存在且未過期且未使用
        cursor.execute("""
            SELECT request_id FROM PasswordResetRequests
            WHERE token = %s AND user_id = %s AND used = 0 AND expiry > UTC_TIMESTAMP()
        """, (token, user_id))
        record = cursor.fetchone()
        if not record:
            return jsonify({"status": "error", "message": "此重設連結無效或已使用"}), 400

        request_id = record[0]

        # 更新密碼
        hashed_pw = generate_password_hash(new_password)
        cursor.execute("""
            UPDATE Users SET password_hash = %s WHERE user_id = %s
        """, (hashed_pw, user_id))

        # 標記 token 已使用
        cursor.execute("""
            UPDATE PasswordResetRequests SET used = 1 WHERE request_id = %s
        """, (request_id,))
        conn.commit()

        return jsonify({"status": "success", "message": "✅ 密碼已重設，請重新登入"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"伺服器錯誤：{str(e)}"}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

@auth_bp.route('/browse')
def browse_page():
    mode = request.args.get('mode', 'unknown')
    keyword = request.args.get('q', '').strip()

    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        if keyword:
            query = """
                SELECT 
                    found_id AS id,
                    item_name AS title,
                    category,
                    found_location AS location,
                    DATE_FORMAT(found_time, '%Y-%m-%d %H:%i:%s') AS date,
                    remark AS description
                FROM FoundItems
                WHERE item_name LIKE %s OR remark LIKE %s OR found_location LIKE %s
                ORDER BY found_time DESC
            """
            params = (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
        else:
            query = """
                SELECT 
                    found_id AS id,
                    item_name AS title,
                    category,
                    found_location AS location,
                    DATE_FORMAT(found_time, '%%Y-%%m-%%d') AS date,
                    remark AS description
                FROM FoundItems
                ORDER BY found_time DESC
            """
            params = ()

        cursor.execute(query, params)
        items = cursor.fetchall()

    except Exception as e:
        print("讀取 FoundItems 錯誤：", e)
        items = []
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

    return render_template('browse.html', mode=mode, items=items)
