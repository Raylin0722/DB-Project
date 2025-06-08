from flask import Blueprint, request, jsonify
from db import connection_pool

match_bp = Blueprint('match', __name__)

@match_bp.route('/api/match')
def match_items():
    lost_id = request.args.get('lost_id')

    if not lost_id:
        return jsonify({'error': '缺少 lost_id 參數'}), 400

    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        # 取得指定失物
        cursor.execute("SELECT * FROM LostItems WHERE lost_id = %s", (lost_id,))
        latest_lost = cursor.fetchone()

        if not latest_lost:
            return jsonify({'error': '找不到指定的失物'}), 404

        # 取得所有拾獲物
        cursor.execute("SELECT * FROM FoundItems")
        found_items = cursor.fetchall()

        return jsonify({
            'latestLost': latest_lost,
            'foundItems': found_items
        })

    except Exception as e:
        return jsonify({'error': f'資料庫錯誤: {str(e)}'}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

@match_bp.route('/api/match/lost_by_found')
def lost_by_found():
    found_id = request.args.get('found_id')
    if not found_id:
        return jsonify({'error': '缺少 found_id 參數'}), 400

    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        # 找到指定的拾獲物
        cursor.execute("SELECT * FROM FoundItems WHERE found_id = %s", (found_id,))
        found_item = cursor.fetchone()
        if not found_item:
            return jsonify({'error': '找不到指定的拾獲物'}), 404

        # 用 found_item 的欄位去找配對失物（名稱、類別、校區、地點、時間都可以當條件）
        cursor.execute("""
            SELECT * FROM LostItems
            WHERE LOWER(item_name) = %s
              AND LOWER(category) = %s
              AND LOWER(lost_campus) = %s
              AND LOWER(lost_location) = %s
              AND lost_time BETWEEN DATE_SUB(%s, INTERVAL 7 DAY) AND DATE_ADD(%s, INTERVAL 7 DAY)
        """, (
            found_item['item_name'].lower(),
            found_item['category'].lower(),
            found_item['found_campus'].lower(),
            found_item['found_location'].lower(),
            found_item['found_time'],
            found_item['found_time']
        ))
        lost_items = cursor.fetchall()

        return jsonify({
            'foundItem': found_item,
            'lostItems': lost_items
        })

    except Exception as e:
        return jsonify({'error': f'資料庫錯誤: {str(e)}'}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

