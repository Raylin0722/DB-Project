from flask import Blueprint, request, jsonify, current_app, url_for, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from db import connection_pool
from datetime import datetime, timedelta
from flask import redirect

profile_bp = Blueprint('profile', __name__)
@profile_bp.route('/profile')
def profile():
    # 這裡示範用 session 取登入者 ID
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        # 取使用者資料
        cursor.execute("SELECT * FROM Users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()

        # 取該使用者刊登的失物紀錄
        cursor.execute("""
            SELECT found_id, item_name, category, found_location,
                   found_time, status
            FROM FoundItems
            WHERE user_id=%s
            ORDER BY found_time DESC
        """, (user_id,))
        posts = cursor.fetchall()

    finally:
        cursor.close(); conn.close()

    return render_template('profile.html', user=user, posts=posts)

@profile_bp.route('/check_edit_profile', methods=['POST', 'GET'])
def check_edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "尚未登入"}), 401

    data = request.get_json()
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Users
            SET username = %s, department = %s, phone = %s
            WHERE user_id = %s
        """, (data['username'], data['department'], data['phone'], user_id))
        conn.commit()

        return jsonify({"status": "success", "message": "資料已更新成功"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close(); conn.close()

@profile_bp.route('/edit_profile', methods=['POST', 'GET'])
def edit_profile():
    return render_template('edit_profile.html')


