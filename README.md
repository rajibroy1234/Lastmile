# 🗺️ LastMile — India Crisis Navigator
## Full Stack Project | 6th Semester

---

## 📁 Project Structure

```
lastmile/
├── app.py              ← Flask API + serves frontend
├── twilio_handler.py   ← SMS gateway setup
├── requirements.txt    ← Python packages
├── static/
│   └── index.html      ← Full frontend (map + UI)
└── README.md
```

> ⚠️ **Important:** Place `index.html` inside a `static/` folder.
> Flask serves it automatically from there.

---

## 🚀 DEPLOY ON RENDER.COM

### STEP 1 — Push to GitHub
```bash
git init
git add .
git commit -m "LastMile deploy"
git remote add origin https://github.com/YOUR_USERNAME/lastmile.git
git push -u origin main
```

### STEP 2 — Create a Web Service on Render
1. Go to [render.com](https://render.com) → **New → Web Service**
2. Connect your GitHub repo
3. Fill in these settings:

| Field | Value |
|-------|-------|
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

### STEP 3 — Set Environment Variables (Optional — Twilio only)
In Render dashboard → **Environment** tab, add:
```
TWILIO_ACCOUNT_SID   = ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN    = your_auth_token
TWILIO_FROM_NUMBER   = +1XXXXXXXXXX
TWILIO_TO_NUMBER     = +91XXXXXXXXXX
```

### STEP 4 — Deploy
Click **Create Web Service**. Render will build and deploy.
Your app will be live at: `https://YOUR-APP-NAME.onrender.com`

---

## 💻 LOCAL DEVELOPMENT

### Install & Run
```bash
pip install -r requirements.txt
python app.py
```
Open: `http://localhost:5000`

---

## 🌐 API ENDPOINTS

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /api/reports | Get all active reports |
| POST   | /api/reports | Submit a new report |
| GET    | /api/shelters | Get all shelters |
| GET    | /api/heatmap | Get heatmap data points |
| GET    | /api/stats | Get live stats |
| POST   | /api/sms | Process SMS report |
| POST   | /api/route | Get safe route |
| PATCH  | /api/reports/<id>/deactivate | Deactivate report |

---

## 📱 SMS SETUP (Twilio)

1. Sign up at https://www.twilio.com (free $15 trial)
2. Get Account SID + Auth Token from console
3. Buy/get a phone number
4. Add credentials as Render environment variables (see Step 3 above)
5. Set webhook URL in Twilio: `https://YOUR-APP-NAME.onrender.com/api/sms`
6. Users text: `FLOOD KAROLBAGH HIGH` → auto-mapped to database

---

## 🛡️ FEATURES

- ✅ Real-time heatmap with Leaflet.js
- ✅ Report submission → saved to SQLite database
- ✅ SMS parsing (FLOOD AREA SEVERITY format)
- ✅ Safe route calculation (avoiding danger zones)
- ✅ Shelter locations with capacity tracking
- ✅ Live stats dashboard
- ✅ Offline mode (cached data)
- ✅ Auto-refresh every 30 seconds
- ✅ Deployed as a single service on Render

---

## 🔧 TECH STACK

- **Backend:** Python, Flask, SQLAlchemy, Gunicorn
- **Database:** SQLite (auto-created on Render disk)
- **Frontend:** HTML, CSS, JavaScript (served by Flask)
- **Map:** Leaflet.js + Leaflet.heat
- **SMS:** Twilio API
- **Hosting:** Render.com

---

*Built for 6th Semester Project | India Crisis Management*
