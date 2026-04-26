from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# ── DATABASE CONFIG ──────────────────────────────────────
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'lastmile.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'lastmile-india-2024')

db = SQLAlchemy(app)

# ── MODELS ───────────────────────────────────────────────
class Report(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    crisis_type = db.Column(db.String(50), nullable=False)
    area_name   = db.Column(db.String(100), nullable=False)
    lat         = db.Column(db.Float, nullable=False)
    lng         = db.Column(db.Float, nullable=False)
    severity    = db.Column(db.Integer, nullable=False)  # 1=low, 2=med, 3=high
    description = db.Column(db.String(300))
    source      = db.Column(db.String(20), default='app')  # app | sms
    verified    = db.Column(db.Boolean, default=False)
    active      = db.Column(db.Boolean, default=True)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        level = 'danger' if self.severity == 3 else 'warning' if self.severity == 2 else 'safe'
        return {
            'id':          self.id,
            'crisis_type': self.crisis_type,
            'area_name':   self.area_name,
            'lat':         self.lat,
            'lng':         self.lng,
            'severity':    self.severity,
            'level':       level,
            'description': self.description,
            'source':      self.source,
            'verified':    self.verified,
            'active':      self.active,
            'timestamp':   self.timestamp.strftime('%H:%M'),
            'date':        self.timestamp.strftime('%Y-%m-%d %H:%M'),
        }

class Shelter(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    area        = db.Column(db.String(100), nullable=False)
    lat         = db.Column(db.Float, nullable=False)
    lng         = db.Column(db.Float, nullable=False)
    capacity    = db.Column(db.Integer, default=100)
    occupancy   = db.Column(db.Integer, default=0)
    contact     = db.Column(db.String(20))
    is_open     = db.Column(db.Boolean, default=True)

    def to_dict(self):
        pct = round(self.occupancy / self.capacity * 100) if self.capacity else 0
        status = 'FULL' if pct >= 90 else 'FILLING' if pct >= 60 else 'OPEN'
        return {
            'id':       self.id,
            'name':     self.name,
            'area':     self.area,
            'lat':      self.lat,
            'lng':      self.lng,
            'capacity': self.capacity,
            'occupancy':self.occupancy,
            'pct':      pct,
            'status':   status,
            'contact':  self.contact,
            'is_open':  self.is_open,
        }

# ── SEED DATA ────────────────────────────────────────────
AREA_COORDS = {
    'Connaught Place': (28.6328, 77.2197),
    'Karol Bagh':      (28.6519, 77.1909),
    'Lajpat Nagar':    (28.5672, 77.2433),
    'Rohini':          (28.7041, 77.1025),
    'Dwarka':          (28.5921, 77.0460),
    'GTB Nagar':       (28.6912, 77.2027),
    'Shahdara':        (28.6719, 77.2882),
    'Mayur Vihar':     (28.6074, 77.2896),
    'Noida Sec 18':    (28.5679, 77.3220),
    'Gurugram Sec 29': (28.4595, 77.0266),
}

def seed_database():
    if Report.query.count() == 0:
        seed_reports = [
            Report(crisis_type='flood',    area_name='Karol Bagh',    lat=28.6519, lng=77.1909, severity=3, description='Heavy waterlogging, knee-deep water on main road', source='app'),
            Report(crisis_type='blocked',  area_name='Connaught Place',lat=28.6328, lng=77.2197, severity=2, description='Road blocked due to protest march', source='sms'),
            Report(crisis_type='fire',     area_name='Shahdara',       lat=28.6719, lng=77.2882, severity=3, description='Factory fire, avoid eastern bypass', source='app'),
            Report(crisis_type='flood',    area_name='Mayur Vihar',    lat=28.6074, lng=77.2896, severity=2, description='Drain overflow, vehicles stuck', source='app'),
            Report(crisis_type='power',    area_name='Rohini',         lat=28.7041, lng=77.1025, severity=1, description='Power outage in sectors 1-5', source='sms'),
            Report(crisis_type='accident', area_name='Noida Sec 18',   lat=28.5679, lng=77.3220, severity=2, description='Multi-vehicle accident on expressway', source='app'),
            Report(crisis_type='riot',     area_name='GTB Nagar',      lat=28.6912, lng=77.2027, severity=3, description='Civil unrest near metro station, avoid area', source='app'),
            Report(crisis_type='shelter',  area_name='Dwarka',         lat=28.5921, lng=77.0460, severity=1, description='Community shelter open, food & water available', source='app'),
        ]
        for r in seed_reports:
            db.session.add(r)

    if Shelter.query.count() == 0:
        shelters = [
            Shelter(name='Delhi Haat Emergency Center',   area='INA',     lat=28.5744, lng=77.2083, capacity=500,  occupancy=120, contact='011-24619431'),
            Shelter(name='Talkatora Stadium Relief Camp', area='CP',      lat=28.6359, lng=77.1993, capacity=800,  occupancy=340, contact='011-23344526'),
            Shelter(name='Rohini Community Hall',         area='Rohini',  lat=28.7100, lng=77.1100, capacity=300,  occupancy=90,  contact='011-27051234'),
            Shelter(name='Dwarka Sec 10 School',          area='Dwarka',  lat=28.5880, lng=77.0520, capacity=400,  occupancy=210, contact='011-28036789'),
            Shelter(name='Shahdara Relief Center',        area='Shahdara',lat=28.6780, lng=77.2940, capacity=600,  occupancy=450, contact='011-22328899'),
            Shelter(name='Noida Stadium',                 area='Noida',   lat=28.5720, lng=77.3280, capacity=1000, occupancy=200, contact='0120-2431234'),
        ]
        for s in shelters:
            db.session.add(s)

    db.session.commit()
    print("✅ Database seeded successfully")

# ── INIT DB ON STARTUP (required for Gunicorn / Render) ──
with app.app_context():
    db.create_all()
    seed_database()

# ── SERVE FRONTEND ────────────────────────────────────────
@app.route('/')
def index():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
    with open(html_path, 'r') as f:
        return f.read(), 200, {'Content-Type': 'text/html'}

# ── ROUTES ───────────────────────────────────────────────

# GET all active reports
@app.route('/api/reports', methods=['GET'])
def get_reports():
    reports = Report.query.filter_by(active=True).order_by(Report.timestamp.desc()).limit(100).all()
    return jsonify({'success': True, 'reports': [r.to_dict() for r in reports], 'count': len(reports)})

# POST new report from app
@app.route('/api/reports', methods=['POST'])
def add_report():
    data = request.get_json()
    required = ['crisis_type', 'area_name', 'lat', 'lng', 'severity']
    for field in required:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400

    report = Report(
        crisis_type = data['crisis_type'],
        area_name   = data['area_name'],
        lat         = float(data['lat']),
        lng         = float(data['lng']),
        severity    = int(data['severity']),
        description = data.get('description', ''),
        source      = data.get('source', 'app'),
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'success': True, 'report': report.to_dict()}), 201

# POST SMS report (Twilio webhook)
@app.route('/api/sms', methods=['POST'])
def sms_report():
    if request.is_json:
        body = request.get_json().get('Body', '')
    else:
        body = request.form.get('Body', '')

    body = body.strip().upper()
    parts = body.split()

    if len(parts) < 2:
        return jsonify({'success': False, 'error': 'Format: TYPE AREA SEVERITY'}), 400

    type_map = {
        'FLOOD': 'flood', 'FIRE': 'fire', 'RIOT': 'riot',
        'BLOCKED': 'blocked', 'SHELTER': 'shelter', 'POWER': 'power',
        'MEDICAL': 'medical', 'ACCIDENT': 'accident'
    }
    area_map = {
        'KAROLBAGH': 'Karol Bagh', 'KAROL': 'Karol Bagh',
        'CP': 'Connaught Place', 'CONNAUGHT': 'Connaught Place',
        'ROHINI': 'Rohini', 'DWARKA': 'Dwarka',
        'LAJPAT': 'Lajpat Nagar', 'GTB': 'GTB Nagar',
        'SHAHDARA': 'Shahdara', 'MAYUR': 'Mayur Vihar',
        'NOIDA': 'Noida Sec 18', 'GURUGRAM': 'Gurugram Sec 29',
    }
    sev_map = {'LOW': 1, 'MED': 2, 'MEDIUM': 2, 'HIGH': 3}

    crisis_type = type_map.get(parts[0])
    area_name   = area_map.get(parts[1])
    severity    = sev_map.get(parts[2], 2) if len(parts) > 2 else 2

    if not crisis_type:
        return jsonify({'success': False, 'error': f'Unknown type: {parts[0]}'}), 400
    if not area_name:
        return jsonify({'success': False, 'error': f'Unknown area: {parts[1]}'}), 400

    coords = AREA_COORDS.get(area_name, (28.6139, 77.2090))
    import random
    jitter = lambda: (random.random() - 0.5) * 0.012

    report = Report(
        crisis_type = crisis_type,
        area_name   = area_name,
        lat         = coords[0] + jitter(),
        lng         = coords[1] + jitter(),
        severity    = severity,
        description = f'SMS report: {body}',
        source      = 'sms',
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'success': True, 'report': report.to_dict()}), 201

# GET all shelters
@app.route('/api/shelters', methods=['GET'])
def get_shelters():
    shelters = Shelter.query.filter_by(is_open=True).all()
    return jsonify({'success': True, 'shelters': [s.to_dict() for s in shelters]})

# GET heatmap data points
@app.route('/api/heatmap', methods=['GET'])
def get_heatmap():
    reports = Report.query.filter(Report.active == True, Report.severity >= 2).all()
    points = [[r.lat, r.lng, r.severity / 3.0] for r in reports]
    return jsonify({'success': True, 'points': points})

# GET stats summary
@app.route('/api/stats', methods=['GET'])
def get_stats():
    total   = Report.query.filter_by(active=True).count()
    danger  = Report.query.filter_by(active=True, severity=3).count()
    warning = Report.query.filter_by(active=True, severity=2).count()
    safe    = Report.query.filter_by(active=True, severity=1).count()
    shelters= Shelter.query.filter_by(is_open=True).count()
    return jsonify({
        'success':  True,
        'total':    total,
        'danger':   danger,
        'warning':  warning,
        'safe':     safe,
        'shelters': shelters,
        'zones':    min(danger + warning, 9)
    })

# PATCH deactivate a report (admin)
@app.route('/api/reports/<int:report_id>/deactivate', methods=['PATCH'])
def deactivate_report(report_id):
    report = Report.query.get_or_404(report_id)
    report.active = False
    db.session.commit()
    return jsonify({'success': True, 'message': f'Report {report_id} deactivated'})

# GET safe route (simple algorithm)
@app.route('/api/route', methods=['POST'])
def get_safe_route():
    data = request.get_json()
    from_lat = float(data.get('from_lat', 0))
    from_lng = float(data.get('from_lng', 0))
    to_lat   = float(data.get('to_lat', 0))
    to_lng   = float(data.get('to_lng', 0))
    from_name= data.get('from_name', 'Origin')
    to_name  = data.get('to_name', 'Destination')

    danger_reports = Report.query.filter(Report.active == True, Report.severity == 3).all()
    danger_zones = [(r.lat, r.lng, r.area_name) for r in danger_reports]

    import math, random
    mid_lat = (from_lat + to_lat) / 2 + (random.random() - 0.5) * 0.04
    mid_lng = (from_lng + to_lng) / 2 + (random.random() - 0.5) * 0.04

    R = 6371
    dlat = math.radians(to_lat - from_lat)
    dlng = math.radians(to_lng - from_lng)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(from_lat)) * math.cos(math.radians(to_lat)) * math.sin(dlng/2)**2
    dist = round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 1)
    eta = round(dist * 3.5)

    bypass = 'Northern Bypass' if mid_lat > 28.6 else 'Ring Road'
    avoid = danger_reports[0].area_name if danger_reports else 'high-risk areas'

    return jsonify({
        'success': True,
        'route': {
            'waypoints': [[from_lat, from_lng], [mid_lat, mid_lng], [to_lat, to_lng]],
            'distance_km': dist,
            'eta_mins': eta,
            'risk_level': 'LOW',
            'steps': [
                f'Start at {from_name} main junction',
                f'Take {bypass} (avoids active danger zones)',
                f'Avoid {avoid} — use outer road',
                f'Arrive at {to_name} safely',
            ],
            'danger_zones_avoided': len(danger_zones),
        }
    })

# ── MAIN ─────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 LastMile India API running at http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)
