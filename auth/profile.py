from flask import Blueprint, request, jsonify, current_app, url_for, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from db import connection_pool
from datetime import datetime, timedelta
from flask import redirect
from collections import defaultdict

profile_bp = Blueprint('profile', __name__)
@profile_bp.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        # 使用者資料
        cursor.execute("SELECT * FROM Users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()

        # 該使用者的遺失物
        cursor.execute("""
            SELECT lost_id, item_name, category, lost_location, lost_time, status, notified_at
            FROM LostItems
            WHERE user_id=%s
            ORDER BY lost_time DESC
        """, (user_id,))
        posts = cursor.fetchall()

        lost_ids = [p['lost_id'] for p in posts]
        match_results = defaultdict(list)

        if lost_ids:
            format_strings = ','.join(['%s'] * len(lost_ids))
            cursor.execute(f"""
                SELECT
                    m.lost_id,
                    m.found_id,
                    DATE_FORMAT(m.match_time, '%Y-%m-%d %H:%i:%S') AS match_time,
                    m.status,
                    f.item_name AS found_name,
                    l.item_name AS lost_name,
                    f.category AS found_category,
                    f.found_location,
                    f.found_time
                FROM Matches m
                JOIN FoundItems f ON m.found_id = f.found_id
                JOIN LostItems l ON m.lost_id = l.lost_id
                WHERE m.lost_id IN ({format_strings})
                AND m.status = 'open'
                ORDER BY m.match_time DESC
            """, tuple(lost_ids))

            for row in cursor.fetchall():
                match_results[row['lost_id']].append(row)

    finally:
        cursor.close(); conn.close()

    return render_template(
        'profile.html',
        user=user,
        posts=posts,
        match_results=match_results  # dict 格式：{lost_id: [匹配項們]}
    )

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

@profile_bp.route('/lost_items/<int:lost_id>/extend', methods=['POST'])
def extend_lost_item(lost_id):
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()

        # 通常延長通知時間：往後延 7 天
        cursor.execute("""
            UPDATE LostItems
            SET notify_at = DATE_ADD(NOW(), INTERVAL 7 DAY),
                notified_at = NULL
            WHERE lost_id = %s
        """, (lost_id,))
        conn.commit()

        return jsonify({'status': 'success', 'message': '延長成功'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        cursor.close()
        conn.close()

@profile_bp.route('/lost_items/<int:lost_id>/delete', methods=['POST'])
def delete_lost_item(lost_id):
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM LostItems WHERE lost_id = %s", (lost_id,))
        conn.commit()

        return jsonify({'status': 'success', 'message': '刪除成功'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        cursor.close()
        conn.close()
