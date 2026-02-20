from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visits.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    # Track the IP before showing the page
    new_visit = Visit(ip=request.remote_addr)
    db.session.add(new_visit)
    db.session.commit()
    # This looks for stats.html inside the 'templates' folder
    return render_template('stats.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Tracker active at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)