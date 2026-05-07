from flask import Flask, request, jsonify, render_template
from urllib.parse import unquote
import mysql.connector
import os

app = Flask(__name__)

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "user":     os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "mysql123"),   # ← change for local use
    "database": os.getenv("DB_NAME", "blood_donation"),
    "port":     int(os.getenv("DB_PORT", 3306))
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def date_to_str(row):
    import datetime
    for k, v in row.items():
        if isinstance(v, (datetime.date, datetime.datetime)):
            row[k] = str(v)
    return row


# ─── Pages ─────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


# ─── API: Search donors using stored procedure ──────────────

@app.route('/search')
def search():
    blood_group = unquote(request.args.get('blood_group', '')).strip()
    city        = unquote(request.args.get('city', '')).strip()

    if not blood_group or not city:
        return jsonify([])

    db     = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.callproc('find_donors', [blood_group, city])
    results = []
    for result in cursor.stored_results():
        results = [date_to_str(r) for r in result.fetchall()]
    cursor.close(); db.close()
    return jsonify(results)


# ─── API: Register a new donor ──────────────────────────────

@app.route('/add_donor', methods=['POST'])
def add_donor():
    db     = get_db()
    cursor = db.cursor(dictionary=True)
    data   = request.form

    phone = data.get('contact', '').strip()
    if not phone.isdigit() or len(phone) != 10:
        cursor.close(); db.close()
        return jsonify({"status": "error", "message": "Phone must be exactly 10 digits."})

    cursor.execute("SELECT donor_id FROM Donor WHERE contact = %s", (phone,))
    if cursor.fetchone():
        cursor.close(); db.close()
        return jsonify({"status": "error", "message": "A donor with this phone number already exists."})

    # Get blood_group_id from blood_type string
    cursor.execute("SELECT blood_group_id FROM Blood_Group WHERE blood_type = %s", (data['blood_group'],))
    bg_row = cursor.fetchone()
    if not bg_row:
        cursor.close(); db.close()
        return jsonify({"status": "error", "message": "Invalid blood group."})

    bg_id = bg_row['blood_group_id']

    cursor.execute(
        """INSERT INTO Donor (name, age, gender, contact, blood_group_id, last_donation, city)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (data['name'], data['age'], data['gender'], phone, bg_id,
         data['last_donation'] or None, data['city'])
    )
    db.commit()
    cursor.close(); db.close()
    return jsonify({"status": "success", "message": "Donor registered successfully!"})


# ─── API: Submit emergency request ─────────────────────────

@app.route('/emergency', methods=['POST'])
def emergency():
    db     = get_db()
    cursor = db.cursor(dictionary=True)
    data   = request.form

    phone = data.get('contact_phone', '').strip()
    if not phone.isdigit() or len(phone) != 10:
        cursor.close(); db.close()
        return jsonify({"status": "error", "message": "Phone must be exactly 10 digits."})

    cursor.execute("SELECT blood_group_id FROM Blood_Group WHERE blood_type = %s", (data['blood_group'],))
    bg_row = cursor.fetchone()
    if not bg_row:
        cursor.close(); db.close()
        return jsonify({"status": "error", "message": "Invalid blood group."})

    bg_id = bg_row['blood_group_id']

    cursor.execute(
        """INSERT INTO Emergency_Request (hospital_name, blood_group_id, required_units, contact_phone, urgency, city)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (data['hospital_name'], bg_id, data.get('required_units', 1),
         phone, data.get('urgency', 'Normal'), data['city'])
    )
    db.commit()
    req_id = cursor.lastrowid

    # Run match procedure to notify donors
    cursor.callproc('match_emergency_donors', [req_id])
    db.commit()

    cursor.close(); db.close()
    return jsonify({"status": "success", "message": "Emergency request submitted! Matching donors notified."})


# ─── API: Blood group stats using cursor procedure ──────────

@app.route('/stats')
def stats():
    db     = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.callproc('get_blood_group_stats')
    results = []
    for result in cursor.stored_results():
        results = result.fetchall()
    cursor.close(); db.close()
    return jsonify(results)


# ─── API: All donors ────────────────────────────────────────

@app.route('/donors')
def donors():
    db     = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            d.donor_id,
            d.name,
            bg.blood_type        AS blood_group,
            d.city,
            d.contact            AS phone,
            d.age,
            d.gender,
            d.last_donation,
            d.is_available,
            fn_days_since_donation(d.donor_id) AS days_since_donation
        FROM   Donor d
        JOIN   Blood_Group bg ON d.blood_group_id = bg.blood_group_id
        ORDER  BY d.name
    """)
    rows = [date_to_str(r) for r in cursor.fetchall()]
    cursor.close(); db.close()
    return jsonify(rows)


# ─── API: All emergency requests ───────────────────────────

@app.route('/requests')
def requests_list():
    db     = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            er.request_id,
            er.hospital_name,
            bg.blood_type   AS blood_group,
            er.required_units,
            er.contact_phone AS phone,
            er.urgency,
            er.status,
            er.city,
            er.request_date
        FROM   Emergency_Request er
        JOIN   Blood_Group bg ON er.blood_group_id = bg.blood_group_id
        ORDER  BY er.request_date DESC
    """)
    rows = [date_to_str(r) for r in cursor.fetchall()]
    cursor.close(); db.close()
    return jsonify(rows)


# ─── API: All donation records ──────────────────────────────

@app.route('/donation_records')
def donation_records():
    db     = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            dr.donation_id,
            d.name          AS donor_name,
            bg.blood_type   AS blood_group,
            dr.donation_date,
            dr.quantity_ml
        FROM   Donation_Record dr
        JOIN   Donor d       ON dr.donor_id       = d.donor_id
        JOIN   Blood_Group bg ON d.blood_group_id = bg.blood_group_id
        ORDER  BY dr.donation_date DESC
    """)
    rows = [date_to_str(r) for r in cursor.fetchall()]
    cursor.close(); db.close()
    return jsonify(rows)


# ─── API: Blood availability stock ─────────────────────────

@app.route('/availability')
def availability():
    db     = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT bg.blood_type, ba.available_units
        FROM   Blood_Availability ba
        JOIN   Blood_Group bg ON ba.blood_group_id = bg.blood_group_id
        ORDER  BY bg.blood_type
    """)
    rows = cursor.fetchall()
    cursor.close(); db.close()
    return jsonify(rows)


# ─── API: Donor notifications ──────────────────────────────

@app.route('/notifications')
def notifications():
    db     = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            dn.notification_id,
            d.name           AS donor_name,
            bg.blood_type    AS blood_group,
            er.hospital_name,
            er.city,
            dn.notification_status,
            dn.notified_at
        FROM   Donor_Notification dn
        JOIN   Donor d            ON dn.donor_id   = d.donor_id
        JOIN   Emergency_Request er ON dn.request_id = er.request_id
        JOIN   Blood_Group bg     ON d.blood_group_id = bg.blood_group_id
        ORDER  BY dn.notified_at DESC
    """)
    rows = [date_to_str(r) for r in cursor.fetchall()]
    cursor.close(); db.close()
    return jsonify(rows)


# ─── API: Update donor donation date (fires trigger) ───────

@app.route('/update_donor', methods=['POST'])
def update_donor():
    db     = get_db()
    cursor = db.cursor(dictionary=True)
    donor_id      = request.form.get('donor_id')
    last_donation = request.form.get('last_donation')

    cursor.execute(
        "UPDATE Donor SET last_donation = %s WHERE donor_id = %s",
        (last_donation, donor_id)
    )
    db.commit()
    cursor.close(); db.close()
    return jsonify({"status": "success", "message": "Donor updated. Trigger recalculated availability."})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)