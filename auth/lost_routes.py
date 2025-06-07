from flask import Blueprint, request, jsonify, current_app, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from db import connection_pool
from datetime import datetime, timedelta

lost_bp = Blueprint('lost', __name__)

@lost_bp.route('/lost_items/create', methods=['POST'])
def create_lost_item():
    data = request.get_json()
    required_fields = ['item_name', 'category', 'lost_campus','lost_location', 'lost_time', 'contact_phone', 'contact_email']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields"}), 400

    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO LostItems 
            (item_name, category,lost_campus, lost_location, lost_time, contact_phone, contact_email, 
             notification_period, remark, status, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['item_name'],
            data['category'],
            data['lost_campus'],
            data['lost_location'],
            data['lost_time'],
            data['contact_phone'],
            data['contact_email'],
            data.get('notification_period', None),
            data.get('remark', ''),
            'open',
            data.get('user_id') 
        ))
        conn.commit()
        return jsonify({"message": "Lost item created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500