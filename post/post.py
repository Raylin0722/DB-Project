from flask import Blueprint, request, jsonify, current_app, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from db import connection_pool
from datetime import datetime, timedelta

post_bp = Blueprint('post', __name__)

@post_bp.route('/browse')
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
                    DATE_FORMAT(found_time, '%Y-%m-%d %H:%i:%s') AS date,
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
    print(items)
    return render_template('browse.html', mode=mode, items=items)
