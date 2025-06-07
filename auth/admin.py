from flask import Blueprint, request, render_template, session, jsonify
from db import connection_pool
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return render_template('ban.html')
        return f(*args, **kwargs)
    return decorated_function

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/adminManage', methods=['GET', 'POST'])
@admin_required
def adminManage():
    mode = request.args.get('mode', 'guest')
    keyword = request.args.get('q', '').strip()

    # 查詢語句模板
    base_query = """
        SELECT 
            {id_col} AS id,
            item_name AS title,
            category,
            {location_col} AS location,
            DATE_FORMAT({time_col}, '%Y-%m-%d %H:%i:%s') AS date,
            remark AS description
        FROM {table}
        {where_clause}
        ORDER BY {time_col} DESC
    """

    if keyword:
        where_clause = "WHERE item_name LIKE %s OR remark LIKE %s OR {location_col} LIKE %s"
        params = (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
    else:
        where_clause = ""
        params = ()

    # 組合查詢
    found_query = base_query.format(
        id_col='found_id',
        location_col='found_location',
        time_col='found_time',
        table='FoundItems',
        where_clause=where_clause.format(location_col='found_location')
    )
    lost_query = base_query.format(
        id_col='lost_id',
        location_col='lost_location',
        time_col='lost_time',
        table='LostItems',
        where_clause=where_clause.format(location_col='lost_location')
    )
    try:
        # 查詢 FoundItems
        conn1 = connection_pool.get_connection()
        cursor1 = conn1.cursor(dictionary=True)
        cursor1.execute(found_query, params)
        found = cursor1.fetchall()

        # 查詢 LostItems
        conn2 = connection_pool.get_connection()
        cursor2 = conn2.cursor(dictionary=True)
        cursor2.execute(lost_query, params)
        lost = cursor2.fetchall()
    except Exception as e:
        print("讀取 FoundItems/LostItems 錯誤：", e)
        found = []
        lost = []
    finally:
        if 'cursor1' in locals(): cursor1.close()
        if 'conn1' in locals(): conn1.close()
        if 'cursor2' in locals(): cursor2.close()
        if 'conn2' in locals(): conn2.close()


    return render_template('manager.html', mode='admin', found=found, lost=lost)

@admin_bp.route('/adminDelete', methods=['GET', 'POST'])
@admin_required
def delete_item():
    target = request.args.get('target')
    item_id = request.args.get('item_id')
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor()
        if target == 'found':
            cursor.execute("DELETE FROM FoundItems WHERE found_id = %s", (item_id,))
        elif target == 'lost':
            cursor.execute("DELETE FROM LostItems WHERE lost_id = %s", (item_id,))
        else:
            return jsonify(success=False, error="未知 target")
        conn.commit()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


