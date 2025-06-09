from flask import Blueprint, request, render_template, session, jsonify
from db import connection_pool
from functools import wraps
import cloudinary.uploader


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return render_template('ban.html')
        return f(*args, **kwargs)
    return decorated_function

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/adminManage', methods=['GET'])
@admin_required
def adminManage():
    # 讀取 mode, keyword
    mode = request.args.get('mode', 'admin')
    keyword = request.args.get('q', '').strip()

    # --- FoundItems SQL ---
    found_sql = """
        SELECT
            found_id      AS id,
            item_name     AS title,
            category,
            found_location AS location,
            DATE_FORMAT(found_time, '%Y-%m-%d %H:%i:%s') AS date,
            remark        AS description
        FROM FoundItems
    """
    if keyword:
        # 簡單把單引號逃脫，然後包成 '%關鍵字%'
        safe = keyword.replace("'", "''")
        found_sql += f"""
        WHERE item_name      LIKE '%{safe}%'
           OR remark         LIKE '%{safe}%'
           OR found_location LIKE '%{safe}%'
        """
    found_sql += " ORDER BY found_time DESC;"

    # --- LostItems SQL ---
    lost_sql = """
        SELECT
            lost_id        AS id,
            item_name      AS title,
            category,
            lost_location  AS location,
            DATE_FORMAT(lost_time, '%Y-%m-%d %H:%i:%s') AS date,
            remark         AS description
        FROM LostItems
    """
    if keyword:
        safe = keyword.replace("'", "''")
        lost_sql += f"""
        WHERE item_name     LIKE '%{safe}%'
           OR remark        LIKE '%{safe}%'
           OR lost_location LIKE '%{safe}%'
        """
    lost_sql += " ORDER BY lost_time DESC;"

    # --- Reports（不過濾關鍵字）---
    report_sql = """
        SELECT
            R.report_id,
            R.description     AS report_description,
            R.status          AS report_status,
            R.created_at      AS report_time,
            F.found_id,
            F.item_name       AS title,
            F.category,
            F.found_location  AS location,
            DATE_FORMAT(F.found_time, '%Y-%m-%d %H:%i:%s') AS date,
            F.remark          AS description
        FROM Reports R
        JOIN FoundItems F ON R.target_id = F.found_id
        ORDER BY R.created_at DESC;
    """

    try:
        # FoundItems
        conn = connection_pool.get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(found_sql)
        found = cur.fetchall()
        cur.close()
        conn.close()

        # LostItems
        conn = connection_pool.get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(lost_sql)
        lost = cur.fetchall()
        cur.close()
        conn.close()

        # Reports
        conn = connection_pool.get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(report_sql)
        report = cur.fetchall()
    except Exception as e:
        print("讀取管理資料錯誤：", e)
        found = []
        lost = []
        report = []
    finally:
        cur.close()
        conn.close()

    return render_template('manager.html',
                           mode=mode,
                           found=found,
                           lost=lost,
                           report=report)

@admin_bp.route('/adminDelete', methods=['GET', 'POST'])
@admin_required
def delete_item():
    target = request.args.get('target')
    item_id = request.args.get('item_id')
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        if target == 'found':
            
            cursor.execute("SELECT cloudinary_id FROM FoundItems WHERE found_id = %s", (item_id,))
            result = cursor.fetchone()
            if result:
                cloudinary_id = result.get('cloudinary_id')
                if cloudinary_id and cloudinary_id.strip():
                    cloudinary.uploader.destroy(cloudinary_id)
                
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


