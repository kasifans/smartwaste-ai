from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from database import init_db, get_all_bins, update_fill_level
from detector import analyze_bin_image
from optimizer import optimize_route
from predictor import predict_all_bins
from alerts import check_and_alert
from pathway_pipeline import start_pipeline_thread

app = Flask(__name__)
CORS(app)

# Initialize database on startup
init_db()

# Start Pathway real-time pipeline
start_pipeline_thread()

# ─────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ─────────────────────────────────────────
# GET ALL BINS
# ─────────────────────────────────────────
@app.route("/api/bins", methods=["GET"])
def get_bins():
    bins = get_all_bins()
    result = []
    for bin in bins:
        result.append({
            "id": bin[0],
            "name": bin[1],
            "location": bin[2],
            "latitude": bin[3],
            "longitude": bin[4],
            "fill_level": bin[5],
            "last_updated": bin[6]
        })
    return jsonify(result)


# ─────────────────────────────────────────
# UPLOAD BIN IMAGE — DETECT FILL LEVEL
# ─────────────────────────────────────────
@app.route("/api/detect", methods=["POST"])
def detect():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    bin_id = request.form.get("bin_id")
    if not bin_id:
        return jsonify({"error": "No bin_id provided"}), 400

    image = request.files["image"]
    image_bytes = image.read()

    # Analyze image
    result = analyze_bin_image(image_bytes)

    # Update database
    update_fill_level(int(bin_id), result["fill_level"])

    # Check if alert needed
    bins = get_all_bins()
    if result["fill_level"] >= 80:
        check_and_alert(bins)

    return jsonify({
        "bin_id": bin_id,
        "fill_level": result["fill_level"],
        "status": result["status"],
        "color": result["color"],
        "action": result["action"]
    })


# ─────────────────────────────────────────
# MANUAL UPDATE FILL LEVEL
# ─────────────────────────────────────────
@app.route("/api/update", methods=["POST"])
def update():
    data = request.get_json()
    bin_id = data.get("bin_id")
    fill_level = data.get("fill_level")

    if not bin_id or fill_level is None:
        return jsonify({"error": "Missing bin_id or fill_level"}), 400

    update_fill_level(int(bin_id), float(fill_level))

    # Send alert if above threshold
    if float(fill_level) >= 80:
        bins = get_all_bins()
        check_and_alert(bins)

    return jsonify({
        "success": True,
        "message": f"Bin {bin_id} updated to {fill_level}%"
    })


# ─────────────────────────────────────────
# OPTIMIZE ROUTE
# ─────────────────────────────────────────
@app.route("/api/optimize", methods=["GET"])
def optimize():
    bins = get_all_bins()
    bin_list = []
    for bin in bins:
        bin_list.append({
            "id": bin[0],
            "name": bin[1],
            "location": bin[2],
            "latitude": bin[3],
            "longitude": bin[4],
            "fill_level": bin[5]
        })

    result = optimize_route(bin_list)
    return jsonify(result)


# ─────────────────────────────────────────
# PREDICT OVERFLOW
# ─────────────────────────────────────────
@app.route("/api/predict", methods=["GET"])
def predict():
    bins = get_all_bins()
    bin_ids = [bin[0] for bin in bins]
    predictions = predict_all_bins(bin_ids)
    return jsonify(predictions)


# ─────────────────────────────────────────
# SEND MANUAL ALERT
# ─────────────────────────────────────────
@app.route("/api/alert", methods=["POST"])
def alert():
    bins = get_all_bins()
    results = check_and_alert(bins)
    return jsonify({
        "success": True,
        "alerts_sent": len(results),
        "details": results
    })


# ─────────────────────────────────────────
# PATHWAY PIPELINE STATUS
# ─────────────────────────────────────────
@app.route("/api/pipeline/status", methods=["GET"])
def pipeline_status():
    return jsonify({
        "status": "RUNNING",
        "message": "Pathway real-time pipeline is active",
        "update_interval": "10 seconds",
        "bins_monitored": 6
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)