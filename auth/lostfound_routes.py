from flask import Blueprint, request, jsonify, current_app, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from db import connection_pool
from datetime import datetime, timedelta

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