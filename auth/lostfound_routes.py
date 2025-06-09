from flask import Blueprint, request, jsonify, current_app, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from db import connection_pool
from datetime import datetime, timedelta
from flask import redirect
from collections import defaultdict

lostfound_bp = Blueprint('lostfound', __name__)

@lostfound_bp.route('/lost_items/create', methods=['POST'])
def create_lost_item():
    data = request.get_json()
    required_fields = ['item_name', 'category', 'lost_campus','lost_location', 'lost_time', 'contact_phone', 'contact_email']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        
        notification_period = int(data.get('notification_period') or 14)
        # notify_at= datetime.now()
        notify_at = datetime.now() + timedelta(days=notification_period - 1)
        
        query = """
            INSERT INTO LostItems 
            (item_name, category,lost_campus, lost_location, lost_time, contact_phone, contact_email, 
             notification_period, remark, status, user_id,notify_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            data['item_name'],
            data['category'],
            data['lost_campus'],
            data['lost_location'],
            data['lost_time'],
            data['contact_phone'],
            data['contact_email'],
            notification_period,
            data.get('remark', ''),
            'open',
            data.get('user_id'),
            notify_at
        ))
        conn.commit()
        newID = cursor.lastrowid
        match_after_insert('lost', newID)
        
        return jsonify({"message": "Lost item created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():cursor.close()
        if 'conn' in locals():conn.close()
    
@lostfound_bp.route('/found_items/create', methods=['POST'])
def create_found_item():
    data = request.get_json()
    required_fields = [
        'item_name', 'category', 'found_campus', 'found_location',
        'found_time', 'storage_location', 'contact_phone', 'contact_email'
    ]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO FoundItems 
            (item_name, image_url,cloudinary_id, category, found_campus, found_location, 
             found_time, storage_location, contact_phone, contact_email, 
             remark, status, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['item_name'],
            data.get('image_url'),
            data.get('cloudinary_id'), 
            data['category'],
            data['found_campus'],
            data['found_location'],
            data['found_time'],
            data['storage_location'],
            data['contact_phone'],
            data['contact_email'],
            data.get('remark', ''),
            'open',
            data.get('user_id')  
        ))
        conn.commit()
        newID = cursor.lastrowid
        match_after_insert('found', newID)
        
        return jsonify({"message": "Found item created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():cursor.close()
        if 'conn' in locals():conn.close()

@lostfound_bp.route('/create_lost')
def create_lost_page():
    return render_template('create_lost.html')

@lostfound_bp.route('/create_found')
def create_found_page():
    return render_template('create_found.html')


def match_items(lost_item, found_item):
    
    if not lost_item or not found_item:
        return False

    # Compare item_name, category, campus, location, and time
    if (lost_item['item_name'].lower() == found_item['item_name'].lower() and
        lost_item['category'].lower() == found_item['category'].lower() and
        lost_item['lost_campus'].lower() == found_item['found_campus'].lower() and
        lost_item['lost_location'].lower() == found_item['found_location'].lower() and
        abs((lost_item['lost_time'] - found_item['found_time']).total_seconds()) <= 3600*12):  # within 1 hour
        return True

    return False


def match_after_insert(item_type, item_id):
    match_result = {}
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    if item_type == 'found':
        # 查出這筆 found
        cursor.execute("SELECT * FROM FoundItems WHERE found_id = %s", (item_id,))
        found = cursor.fetchone()
        # 查所有 lost
        cursor.execute("SELECT * FROM LostItems")
        lost_list = cursor.fetchall()
        # 配對
        for lost in lost_list:
            if match_items(lost, found):
                match_result.setdefault(lost['lost_id'], []).append(found['found_id'])
                print(f"Found {found['found_id']} 配對 Lost {lost['lost_id']}")
    elif item_type == 'lost':
        cursor.execute("SELECT * FROM LostItems WHERE lost_id = %s", (item_id,))
        lost = cursor.fetchone()
        cursor.execute("SELECT * FROM FoundItems")
        found_list = cursor.fetchall()
        for found in found_list:
            if match_items(lost, found):
                match_result.setdefault(lost['lost_id'], []).append(found['found_id'])
                    
                print(f"Lost {lost['lost_id']} 配對 Found {found['found_id']}")
    
    
    if match_result:
        for lost_id, found_ids in match_result.items():
            cursor.execute("""SELECT U.username, U.school_email
            FROM LostItems L
            JOIN Users U ON L.user_id = U.user_id
            WHERE L.lost_id = %s;""", (lost_id,))
            result = cursor.fetchone()
            for found_id in found_ids:
                cursor.execute(
                    """INSERT INTO Matches(lost_id, found_id, match_time, status)
                    VALUES (%s, %s, NOW(), 'open')""",
                    (lost_id, found_id)
                )
            conn.commit()
            if result:
                send_match_email(result)

    if 'cursor' in locals(): cursor.close()
    if 'conn' in locals(): conn.close()


def send_match_email(result):
    
    email = result['school_email']
    username = result['username']


    msg = Message('師大校園失物招領系統 配對成功通知', recipients=[email])
    msg.body = f'''您好 {username}:

    您登記的物品已有初步配對結果，請盡快上系統網頁確認配對項目是否正確。

    若配對正確，請依系統指示完成後續領取流程。

    如有疑問，請聯繫系統管理員或客服信箱。

    謝謝您使用本系統！

    師大校園失物招領系統 敬上

    此信件由系統自動發出，請勿回覆本信件'''

    current_app.mail.send(msg)
    
@lostfound_bp.route('/match/<int:lost_id>/<int:found_id>/confirm', methods=['POST'])
def confirm_match(lost_id, found_id):
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()

        # 1. 更新該筆為 confirmed
        cursor.execute("""
            UPDATE Matches
            SET status = 'confirmed'
            WHERE lost_id = %s AND found_id = %s AND status = 'open'
        """, (lost_id, found_id))

        # 2. 刪除其他相同 lost_id 的未中選配對
        cursor.execute("""
            DELETE FROM Matches
            WHERE lost_id = %s AND found_id != %s AND status = 'open'
        """, (lost_id, found_id))

        # 3. 更新 LostItems 的狀態為 confirmed
        cursor.execute("""
            UPDATE LostItems
            SET status = 'confirmed'
            WHERE lost_id = %s
        """, (lost_id,))
        
        cursor.execute("""
            UPDATE FoundItems
            SET status = 'confirmed'
            WHERE found_id = %s
        """, (found_id,))

        conn.commit()
        return redirect('/profile')

    except Exception as e:
        return f"更新錯誤：{e}", 500
    finally:
        cursor.close(); conn.close()

@lostfound_bp.route('/match/<int:lost_id>/<int:found_id>/delete', methods=['POST'])
def delete_match(lost_id, found_id):
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM Matches
            WHERE lost_id = %s AND found_id = %s AND status = 'open'
        """, (lost_id, found_id))
        conn.commit()
        return redirect('/profile')

    except Exception as e:
        return f"刪除錯誤：{e}", 500
    finally:
        cursor.close(); conn.close()
        
@lostfound_bp.route('/tasks/notify', methods=['GET'])
def run_notify_task():
    token = request.args.get('token')
    if token != current_app.config['CRON_TOKEN']:
        return jsonify({'status': 'unauthorized'}), 403
    try:
        notify_expiring_lost_items()
        return jsonify({'status': 'success', 'message': '提醒信已寄出'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@lostfound_bp.route('/tasks/cleanup', methods=['GET'])
def run_cleanup_task():
    token = request.args.get('token')
    if token != current_app.config['CRON_TOKEN']:
        return jsonify({'status': 'unauthorized'}), 403
    try:
        delete_expired_lost_items()
        return jsonify({'status': 'success', 'message': '過期資料已清除'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500   
    
def notify_expiring_lost_items():
    conn = connection_pool.get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT L.*, U.school_email, U.username
            FROM LostItems L
            JOIN Users U ON L.user_id = U.user_id
            WHERE L.status = 'open'
            AND notify_at IS NOT NULL
            AND notify_at <= NOW()
        """)
        expiring_items = cursor.fetchall()

        for item in expiring_items:
            msg = Message('失物登記即將到期提醒', recipients=[item['school_email']])
            msg.body = f'''
                您好 {item['username']}，

                您在校園失物招領系統登記的物品「{item['item_name']}」即將在一天後到期。

                請於 24 小時內登入系統確認是否要延長登記時間，
                否則該筆資料將會自動從系統中刪除。
                
                請登入後點擊"個人資訊"，至"我的遺失物登記紀錄"進行延長。

                登入系統: https://lostfoundntnu.up.railway.app/

                謝謝您使用本系統！

                師大校園失物招領系統 敬上

                此信件由系統自動發出，請勿回覆本信件
            '''
            current_app.mail.send(msg)

            # 標記已通知
            cursor.execute("""
                UPDATE LostItems SET notified_at = NOW()
                WHERE lost_id = %s
            """, (item['lost_id'],))

        conn.commit()

    except Exception as e:
        print('[通知失敗]', str(e))
    finally:
        cursor.close()
        conn.close()
        
def delete_expired_lost_items():
    conn = connection_pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM LostItems
            WHERE notified_at IS NOT NULL
            AND notified_at <= NOW() - INTERVAL 1 DAY
            AND status = 'open'
        """)
        conn.commit()

    except Exception as e:
        print('[刪除失敗]', str(e))
    finally:
        cursor.close()
        conn.close()
