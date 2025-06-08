from flask import Blueprint, request, jsonify, current_app, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from db import connection_pool
from datetime import datetime, timedelta

post_bp = Blueprint('post', __name__)

@post_bp.route('/browse')
def browse_page():
    mode = request.args.get('mode', 'guest')
    keyword = request.args.get('q', '').strip()
    
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)


        print(keyword)
        if keyword:
            query = """
                SELECT 
                    found_id AS id,
                    item_name AS title,
                    category,
                    found_location AS location,
                    DATE_FORMAT(found_time, '%%Y-%%m-%%d %%H:%%i:%%s') AS date,
                    remark AS description
                FROM FoundItems
                WHERE item_name LIKE %s OR remark LIKE %s OR found_location LIKE %s
                ORDER BY found_time DESC
            """
            params = (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%')
            print(params)
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
   
    return render_template('browse.html', mode=mode, items=items)
@post_bp.route('/reportitems')
def report_post():
    fid = request.args.get('fid')
    rid = request.args.get('rid')
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
                
        cursor.execute("""SELECT 
                R.report_id,
                R.description AS report_description,
                R.status AS report_status,
                R.created_at AS report_time,
                F.found_id,
                F.found_location,
                F.found_time AS found_time,
                F.item_name AS title,
                F.category,
                F.remark,
                F.image_url,
                F.found_campus,
                F.storage_location,
                F.contact_phone,
                F.contact_email,
                F.status AS found_status
            FROM Reports R
            JOIN FoundItems F ON R.target_id = F.found_id
            where R.report_id = %s
            ORDER BY R.created_at DESC;""", (rid,))
        report = cursor.fetchone()
        
    except Exception as e:
        print("讀取報告項目錯誤：", e)
        return render_template('admin_report.html', item=[])
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
    print(report)
    return render_template('admin_report.html', item=report, from_page="adminManage")

@post_bp.route('/send_report', methods=['POST'])
def send_report():
    mode = request.form.get('mode')
    rid = request.form.get('rid')
    reasons = request.form.getlist('reasons')
    print(reasons)
    if not mode or not rid or not reasons:
        return jsonify({"status": "error", "message": "缺少必要參數"}, 400)
    if mode == 'accept':
        try:
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Reports SET status = 'accept', description=%s WHERE report_id = %s", (reasons[0], rid))
            conn.commit()
            cursor.execute("""
                SELECT u.school_email, f.item_name, r.description
                FROM Reports r
                JOIN FoundItems f ON r.target_id = f.found_id
                JOIN Users u ON f.user_id = u.user_id
                WHERE r.report_id = %s
            """, (rid,))
            result = cursor.fetchone()
            if result:
                recipient_email = result[0]
                item_name = result[1]
                report_description = result[2]

                msg = Message(subject="您的失物貼文被檢舉並確認",
                              recipients=[recipient_email])
                msg.body = f"您好，\n\n您的失物貼文「{item_name}」已被檢舉，經審核後確定違反規則，故已處理下架或標記。\n檢舉原因為：{report_description}。\n\n如有疑問請聯繫系統管理員。"
                current_app.mail.send(msg)

                print("準備寄信給：", recipient_email)
            else:
                print("找不到對應的用戶或貼文")
        except Exception as e:
            print("更新報告狀態錯誤：", e)
            return jsonify({"status": "error", "message": "更新報告狀態失敗"}), 500
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
    

    
    
    elif mode == 'reject':
        try:
            conn = connection_pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE Reports SET status = 'reject', description=%s WHERE report_id = %s", (reasons[0], rid))
            conn.commit()
        except Exception as e:
            print("更新報告狀態錯誤：", e)
            return jsonify({"status": "error", "message": "更新報告狀態失敗"}), 500
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
        
    else:
        return jsonify({"status": "error", "message": "未知的模式"}), 400
    print("送出檢舉：", mode, rid, reasons)
    return jsonify({"status": "success"}), 200


@post_bp.route('/report', methods=['POST'])
def report():
    fid = request.form.get('fid')
    reasons = request.form.getlist('reasons')
    
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Reports WHERE target_id = %s and status='accept'", (fid,))
        existing_report = cursor.fetchall()
        if existing_report:
            return jsonify({"status": "success", "message": "此失物項目已被檢舉"}), 400
    except Exception as e:
        print("讀取失物項目錯誤：", e)
        return jsonify({"status": "error", "message": "讀取失物項目失敗"}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
        
    
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            insert into Reports (target_id, description, status, created_at)
            values (%s, %s, 'open', NOW())
        """, (fid, reasons[0]))
        conn.commit()
        
    except Exception as e:
        print("寫入失物項目錯誤：", e)
        return jsonify({"status": "error", "message": "寫入失物項目失敗"}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

    return jsonify({"status": "success", "message": "檢舉成功"}), 200