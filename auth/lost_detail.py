
from PIL import Image
import io
import traceback
from flask import Blueprint, request, jsonify, current_app, url_for, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from db import connection_pool
from datetime import datetime, timedelta

lost_detail_bp = Blueprint('lost_detail', __name__)
@lost_detail_bp.route('/lostitems/<int:item_id>')
def item_detail(item_id):
    from_page = request.args.get('from_page', 'browse')
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                lost_id, item_name, category, lost_campus,
                lost_location, lost_time,
                contact_phone, contact_email, remark, status
            FROM LostItems
            WHERE lost_id = %s
        """, (item_id,))
        item = cursor.fetchone()

        if not item:
            return "查無此項目", 404

    except Exception as e:
        print("讀取 item 詳情錯誤：", e)
        return "伺服器錯誤", 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

    return render_template('lost_detail.html', item=item, from_page=from_page)
