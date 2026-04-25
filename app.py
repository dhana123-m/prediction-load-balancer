from flask import Flask, render_template, jsonify
from flask import request, redirect, session,url_for
from flask_socketio import SocketIO
from flask import send_file
from monitor import get_metrics
from database import db, cursor
from balancer import balance_system
from protection import detect_risk
from cleanup import clean_temp
from process_guard import (
    detect_heavy_user_app,
    top_process
)

import pickle
import pandas as pd
import time

app = Flask(__name__)

app.secret_key = "sysguard_secret_key"

# SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# ML Model
model = pickle.load(open("model.pkl", "rb"))

# Prevent repeated actions
last_alert_time = 0


# ===============================
# LOGIN / SESSION ROUTES
# ===============================

@app.route('/')
def home():

    if 'user' in session:
        return redirect('/dashboard')

    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        sql = """
        SELECT username, role
        FROM users
        WHERE username=%s AND password=%s
        """

        cursor.execute(sql, (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = user[0]
            session['role'] = user[1]
            return redirect('/dashboard')

        return render_template("login.html", error="Invalid Login")

    return render_template("login.html")


@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/')

    return render_template(
        "dashboard.html",
        username=session['user'],
        role=session['role']
    )

@app.route('/settings')
def settings():

    if 'user' not in session:
        return redirect('/')

    if session['role'] != "Admin":
        return "Access Denied"

    return render_template("settings.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ===============================
# LIVE METRICS API
# ===============================

@app.route('/metrics')
def metrics():
    global last_alert_time

    try:
        # Live system metrics
        cpu, ram, disk, network, battery, temp = get_metrics()

        # Heavy process detection
        heavy_name = "None"
        heavy_cpu = 0
        heavy_pid = 0

        try:
            heavy_name, heavy_cpu, heavy_pid = top_process()
        except:
            pass

        # Warning mode only
        warning_message = "No Warning"

        try:
            app_name, pid, app_cpu = detect_heavy_user_app()

            if pid:
                warning_message = (
                    f"{app_name} using {app_cpu}% CPU. "
                    f"Recommended: Close application."
                )

        except:
            pass

        # Save metrics to database
        try:
            sql = """
            INSERT INTO system_metrics
            (cpu, ram, disk, network, battery, temp, heavy_app, heavy_cpu)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """

            values = (
                cpu,
                ram,
                disk,
                network,
                battery,
                temp,
                heavy_name,
                heavy_cpu
            )

            cursor.execute(sql, values)
            db.commit()

        except:
            pass

        # ML Prediction
        sample = pd.DataFrame(
            [[cpu, ram, disk]],
            columns=["cpu", "ram", "disk"]
        )

        prediction = model.predict(sample)[0]

        # Load balancing
        status = balance_system(prediction)

        # Risk detection
        risk = detect_risk(cpu, ram, disk)

        # Cleanup mode
        cleanup_status = "No Action"

        if risk == "Critical":

            cleanup_status = clean_temp()

            current_time = time.time()

            if current_time - last_alert_time > 600:
                last_alert_time = current_time

        # Final JSON data
        data = {
            "cpu": cpu,
            "ram": ram,
            "disk": disk,
            "network": network,

            "battery": battery,
            "temp": temp,

            "prediction": prediction,
            "status": status,
            "risk": risk,

            "heavy_name": heavy_name,
            "heavy_cpu": heavy_cpu,
            "heavy_pid": heavy_pid,

            "warning_message": warning_message,
            "cleanup_status": cleanup_status
        }

        # Real-time Socket Push
        socketio.emit("metrics_update", data)

        return jsonify(data)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

@app.route('/report')
def report():

    if 'user' not in session:
        return redirect('/')

    from reportlab.pdfgen import canvas

    filename = "system_report.pdf"

    c = canvas.Canvas(filename)

    c.setFont("Helvetica-Bold",16)
    c.drawString(180,800,"SysGuard AI Report")

    c.setFont("Helvetica",12)
    c.drawString(50,760,"Generated By: " + session['user'])
    c.drawString(50,740,"Role: " + session['role'])

    c.drawString(50,700,"System Monitoring Summary")
    c.drawString(50,680,"CPU monitored successfully")
    c.drawString(50,660,"RAM monitored successfully")
    c.drawString(50,640,"Risk engine active")

    c.save()

    return send_file(filename, as_attachment=True)

@app.route('/reports')
def reports():

    if 'user' not in session:
        return redirect('/')

    return render_template(
        "reports.html",
        username=session['user'],
        role=session['role']
    )


@app.route('/protection')
def protection():

    if 'user' not in session:
        return redirect('/')

    cpu, ram, disk, network, battery, temp = get_metrics()

    risk = detect_risk(cpu, ram, disk)

    # Live threat status
    if risk == "Critical":
        threat = "Critical Threat Detected"
    elif risk == "Warning":
        threat = "Performance Warning"
    else:
        threat = "No Active Threat"

    # Real alert count from DB
    cursor.execute("""
        SELECT COUNT(*)
        FROM system_metrics
        WHERE cpu > 85 OR ram > 85 OR disk > 90
    """)

    count = cursor.fetchone()[0]

    return render_template(
        "protection.html",
        username=session['user'],
        role=session['role'],
        threat=threat,
        count=count
    )
    
@app.route('/cleanup-now')
def cleanup_now():

    if 'user' not in session:
        return redirect('/')

    clean_temp()

    return redirect('/protection')

@app.route('/scan-now')
def scan_now():

    cpu, ram, disk, network, battery, temp = get_metrics()
    risk = detect_risk(cpu, ram, disk)

    return render_template(
        "scan.html",
        cpu=cpu,
        ram=ram,
        disk=disk,
        risk=risk,
        battery=battery,
        temp=temp
    )
# ===============================
# RUN APP
# ===============================

if __name__ == '__main__':
    socketio.run(
        app,
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )