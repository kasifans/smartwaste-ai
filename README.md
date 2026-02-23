# 🗑️ SmartWaste AI
### AI-Powered Smart Waste Management System for Indian Municipalities

Built for Noida municipal infrastructure to reduce bin overflow and optimize garbage truck routes using real-time AI monitoring.

---

## 🚀 Features

- 📍 **Live Bin Tracking** — Real-time bin status on interactive Noida map
- 🤖 **AI Fill Detection** — Upload bin image, OpenCV detects fill level instantly
- ⚡ **Route Optimization** — Google OR-Tools calculates shortest collection route
- 🚨 **WhatsApp Alerts** — Automatic driver notification via Twilio when bin crosses 80%
- 📊 **Predictive Analytics** — Estimates when each bin will overflow based on fill rate
- 🌙 **Professional Dashboard** — Dark theme, mobile responsive, live auto-refresh

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| AI / Vision | OpenCV, NumPy |
| Optimization | Google OR-Tools |
| Alerts | Twilio WhatsApp API |
| Frontend | JavaScript, CSS3 |
| Map | Leaflet.js, OpenStreetMap |
| Database | SQLite |
| Deployment | Render |

---

## 📦 Installation
```bash
# Clone the repository
git clone https://github.com/kasifans/smartwaste-ai.git
cd smartwaste-ai

# Install dependencies
pip install -r requirements.txt

# Setup config
cp config.example.py config.py
# Edit config.py with your Twilio credentials

# Run the app
python app.py
```

---

## ⚙️ Configuration

Copy `config.example.py` to `config.py` and fill in:
```python
TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_WHATSAPP_FROM = "+14155238886"
DRIVER_PHONE_NUMBER = "+91XXXXXXXXXX"
```

---

## 🗺️ System Architecture
```
📷 Bin Image Upload
        ↓
OpenCV Fill Detection
        ↓
Flask Backend + SQLite
        ↓
Overflow Prediction Engine
        ↓
OR-Tools Route Optimizer
        ↓
Live Dashboard + Map
        ↓
WhatsApp Alert to Driver
```

---

## 🌍 Impact

- Reduces bin overflow by up to 60%
- Cuts fuel waste through optimized routes
- Real-time visibility for municipal authorities
- Scalable to any Indian city

---

## 👨‍💻 Developer

**Mohammad Kasif**
Final Year B.Tech CSE
GitHub: [@kasifans](https://github.com/kasifans)

---

## 📄 License

MIT License — Free to use and modify