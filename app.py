from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configuration for SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visits.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- DATABASE INITIALIZATION ---
# This block runs when Gunicorn or Python starts the app
with app.app_context():
    db.create_all()
    print("Database tables initialized successfully.")

# --- Tracking Logic ---
@app.before_request
def track_ip():
    # Only track the main page to keep data clean
    if request.endpoint == 'index':
        # Get real IP from 'X-Forwarded-For' (for Render/Cloud)
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        
        new_visit = Visit(ip=ip)
        db.session.add(new_visit)
        db.session.commit()

# --- Routes ---
@app.route('/')
def index():
    return render_template('stats.html')

@app.route('/api/stats')
def get_stats_api():
    from sqlalchemy import func
    results = db.session.query(
        Visit.ip, 
        func.count(Visit.id).label('count'),
        func.max(Visit.timestamp).label('last_seen')
    ).group_by(Visit.ip).order_by(func.count(Visit.id).desc()).all()

    data = []
    for ip, count, last_seen in results:
        data.append({
            'ip': ip,
            'count': count,
            'last_seen': last_seen.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
