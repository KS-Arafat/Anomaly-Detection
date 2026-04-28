"""
SafeNest Guard — Complete Backend Server
=========================================
ONE file. Replaces safenest_api.py + safenest_pi_bridge.py.

WHAT THIS DOES:
  ✅ Loads all trained models
  ✅ Flask HTTP API — scenario buttons call this
  ✅ Publishes results to HiveMQ MQTT → dashboard updates live
  ✅ Sends Bangla Telegram alerts on THREAT/WATCH
  ✅ Background Pi bridge loop (auto-runs every 5s)

INSTALL:
  pip3 install flask flask-cors paho-mqtt joblib numpy scikit-learn xgboost tensorflow --break-system-packages

RUN:
  python3 safenest_server.py

THEN open safenest_dashboard_final.html in your browser.
"""

import json, time, os, threading, logging
from dotenv import load_dotenv
import numpy as np
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("SafeNest")

# Configure Flask to find templates in the current directory
import os as _os_init

app = Flask(
    __name__, template_folder=_os_init.path.dirname(_os_init.path.abspath(__file__))
)
CORS(app)

# ╔══════════════════════════════════════════════════════════╗
# ║           FILL IN YOUR CREDENTIALS HERE                 ║
# ╚══════════════════════════════════════════════════════════╝

# Model folder — change to match where your files are
# Colab/Drive: '/content/drive/MyDrive/cse499/Datasets/SafeNest_Final_Output'
# Pi:          '/home/pi/SafeNest_Final_Output'
# Windows:     'C:/Users/YourName/Downloads/SafeNest_Final_Output'
MODEL_DIR = "./SafeNest_Models"

load_dotenv()
# HiveMQ — get from hivemq.com (free cloud account)
MQTT_HOST = os.environ["MQTT_HOST"]
MQTT_USER = os.environ["MQTT_USER"]
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]
MQTT_PORT = int(os.environ["MQTT_PORT"])
MQTT_TOPIC = os.environ["MQTT_TOPIC"]

# Telegram — token from @BotFather, chat_id from @userinfobot
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# ╚══════════════════════════════════════════════════════════╝

# ── Load models ───────────────────────────────────────────────────────────────
PIPELINE_LOADED = False
FEAT_COLS = []
gru_model = None
ZD_W = {"if": 0.5, "ae": 0.5, "gru": 0.0}

try:
    import joblib, tensorflow as tf

    tf.get_logger().setLevel("ERROR")

    scaler = joblib.load(f"{MODEL_DIR}/scaler.pkl")
    rf = joblib.load(f"{MODEL_DIR}/model_rf.pkl")
    xgb_m = joblib.load(f"{MODEL_DIR}/model_xgb.pkl")
    cal_rf = joblib.load(f"{MODEL_DIR}/calibrator_rf.pkl")
    cal_xgb = joblib.load(f"{MODEL_DIR}/calibrator_xgb.pkl")
    cal_zd = joblib.load(f"{MODEL_DIR}/calibrator_zd.pkl")
    le = joblib.load(f"{MODEL_DIR}/label_encoder.pkl")
    ae = tf.keras.models.load_model(f"{MODEL_DIR}/autoencoder.keras")
    if_model = joblib.load(f"{MODEL_DIR}/model_if.pkl")

    gru_path = f"{MODEL_DIR}/gru_temporal.keras"
    gru_model = (
        tf.keras.models.load_model(gru_path) if os.path.exists(gru_path) else None
    )

    with open(f"{MODEL_DIR}/feature_names.json") as f:
        FEAT_COLS = json.load(f)
    with open(f"{MODEL_DIR}/if_norm_bounds.json") as f:
        b = json.load(f)
        IF_MIN, IF_MAX = b["min"], b["max"]
    with open(f"{MODEL_DIR}/ae_threshold.json") as f:
        b = json.load(f)
        AE_MIN, AE_MAX = b["min"], b["max"]

    if gru_model:
        with open(f"{MODEL_DIR}/gru_norm_bounds.json") as f:
            b = json.load(f)
            GRU_MIN, GRU_MAX = b["min"], b["max"]
        with open(f"{MODEL_DIR}/zd_weights.json") as f:
            ZD_W = json.load(f)

    BENIGN_IDX = list(le.classes_).index("BenignTraffic")
    PIPELINE_LOADED = True
    log.info(
        f"✅ Pipeline loaded | {len(FEAT_COLS)} features | {len(le.classes_)} classes"
    )
    log.info(f'   GRU: {"loaded" if gru_model else "not found — using IF+AE only"}')

except Exception as e:
    log.warning(f"⚠️  Models not loaded — DEMO MODE active")
    log.warning(f"   Error: {e}")
    log.warning(f"   Fix MODEL_DIR above to point to your SafeNest_Final_Output folder")


# ── TRAV 2.0 ──────────────────────────────────────────────────────────────────
class TRAV2:
    def __init__(self):
        self.history = {}
        self.W = {"B": 0.30, "T": 0.20, "G": 0.20, "P": 0.15, "D": 0.15}

    def evaluate(self, dev, s):
        h = self.history.get(dev, [])
        if len(h) >= 2:
            med = np.median([x["bw"] for x in h])
            B = float(np.clip(1 - abs(s["bw"] - med) / (med + 1e-6), 0, 1))
        else:
            B = 0.5
        G = float(s.get("geo_asn_trust", 0.5))
        P = float(s.get("peer_corr", 0.5))
        return float(
            self.W["B"] * B
            + self.W["T"] * 0.5
            + self.W["G"] * G
            + self.W["P"] * P
            + self.W["D"] * 0.5
        )

    def update(self, dev, s):
        h = self.history.get(dev, [])
        h.append(s)
        self.history[dev] = h[-7:]

    def reset(self, dev=None):
        if dev:
            self.history[dev] = []
        else:
            self.history = {}


trav = TRAV2()

# Seed TRAV with 5 benign sessions so it has a baseline
for _dev in ["home_camera", "home_router", "home_lock"]:
    for _ in range(5):
        trav.update(
            _dev, {"bw": 1000, "hour": 20, "geo_asn_trust": 0.9, "peer_corr": 0.9}
        )


# ── Decision engine ───────────────────────────────────────────────────────────
def decide(cwf_prob, trust, zd_score, device_age=30):
    if device_age < 7:
        return "WATCH", "new_device_profiling"
    if cwf_prob >= 0.90 and trust < 0.50:
        return "THREAT", "high_confidence_attack"
    if cwf_prob >= 0.70 and trust >= 0.80:
        return "WATCH", "trusted_owner_anomaly"
    if cwf_prob >= 0.70 and trust < 0.80:
        return "THREAT", "attack_no_trust"
    if cwf_prob >= 0.45 or (zd_score >= 0.85 and cwf_prob >= 0.30):
        return "WATCH", "elevated_concern"
    return "SAFE", "normal_traffic"


# ── Core inference ────────────────────────────────────────────────────────────
def run_inference(
    flow_dict, device_id="home_camera", trav_overrides=None, device_age=30
):
    if not PIPELINE_LOADED:
        # Demo mode — return realistic fixed values
        is_attack = trav_overrides and trav_overrides.get("geo_asn_trust", 0.9) < 0.4
        cwf = 0.991 if is_attack else 0.008
        tr = trav_overrides.get("geo_asn_trust", 0.95) if trav_overrides else 0.95
        dec, reason = decide(cwf, tr, cwf * 0.9, device_age)
        return {
            "device_id": device_id,
            "decision": dec,
            "reason": reason,
            "cwf_prob": round(cwf, 3),
            "trust": round(tr, 3),
            "pred_class": "DDoS-SYN_Flood" if is_attack else "BenignTraffic",
            "zd": round(cwf * 0.9, 3),
            "rf_att": round(cwf, 3),
            "xgb_att": round(cwf, 3),
            "timestamp": time.time(),
            "pipeline_loaded": False,
        }

    x = np.array([[flow_dict.get(c, 0.0) for c in FEAT_COLS]], dtype=np.float32)
    x_s = np.clip(scaler.transform(x), -10, 10).astype(np.float32)

    rf_att = float(cal_rf.transform([1 - rf.predict_proba(x_s)[0, BENIGN_IDX]])[0])
    xgb_att = float(cal_xgb.transform([1 - xgb_m.predict_proba(x_s)[0, BENIGN_IDX]])[0])

    if_raw = float(-if_model.score_samples(x_s)[0])
    if_norm = float(np.clip((if_raw - IF_MIN) / (IF_MAX - IF_MIN + 1e-9), 0, 1))
    ae_raw = float(np.mean((ae(x_s, training=False).numpy() - x_s) ** 2))
    ae_norm = float(np.clip((ae_raw - AE_MIN) / (AE_MAX - AE_MIN + 1e-9), 0, 1))

    gru_norm = 0.0
    if gru_model:
        rng = np.random.RandomState(42)
        jit = rng.uniform(-0.05, 0.05, (1, 8, x_s.shape[1])).astype(np.float32)
        seq = np.broadcast_to(x_s[:, None, :], (1, 8, x_s.shape[1])).copy() + jit
        gru_raw = float(np.mean((gru_model(seq, training=False).numpy() - x_s) ** 2))
        gru_norm = float(
            np.clip((gru_raw - GRU_MIN) / (GRU_MAX - GRU_MIN + 1e-9), 0, 1)
        )

    zd_raw = ZD_W["if"] * if_norm + ZD_W["ae"] * ae_norm + ZD_W["gru"] * gru_norm
    zd_cal = float(cal_zd.transform([zd_raw])[0])
    cwf_prob = float(0.5 * rf_att + 0.3 * xgb_att + 0.2 * zd_cal)

    trav_session = {
        "bw": float(flow_dict.get("flow_pkts_per_sec", 1000)),
        "hour": float(time.localtime().tm_hour),
        "geo_asn_trust": float((trav_overrides or {}).get("geo_asn_trust", 0.7)),
        "peer_corr": float((trav_overrides or {}).get("peer_corr", 0.7)),
    }
    trust = trav.evaluate(device_id, trav_session)
    trav.update(device_id, trav_session)

    pred_class = le.classes_[int(rf.predict(x_s)[0])]
    decision, reason = decide(cwf_prob, trust, zd_cal, device_age)

    return {
        "device_id": device_id,
        "decision": decision,
        "reason": reason,
        "cwf_prob": round(cwf_prob, 4),
        "trust": round(trust, 4),
        "pred_class": pred_class,
        "zd": round(zd_cal, 4),
        "rf_att": round(rf_att, 4),
        "xgb_att": round(xgb_att, 4),
        "timestamp": time.time(),
        "pipeline_loaded": True,
    }


# ── State ─────────────────────────────────────────────────────────────────────
EVENT_LOG = []
DEVICE_STATE = {
    "home_camera": {
        "decision": "SAFE",
        "trust": 0.97,
        "cwf_prob": 0.004,
        "zd": 0.076,
        "pred_class": "BenignTraffic",
        "last_seen": time.time(),
    },
    "home_router": {
        "decision": "SAFE",
        "trust": 0.95,
        "cwf_prob": 0.008,
        "zd": 0.091,
        "pred_class": "BenignTraffic",
        "last_seen": time.time(),
    },
    "home_lock": {
        "decision": "SAFE",
        "trust": 0.93,
        "cwf_prob": 0.002,
        "zd": 0.063,
        "pred_class": "BenignTraffic",
        "last_seen": time.time(),
    },
}


def save_event(result):
    EVENT_LOG.append(result)
    if len(EVENT_LOG) > 300:
        EVENT_LOG.pop(0)
    DEVICE_STATE[result["device_id"]] = {
        "decision": result["decision"],
        "trust": result["trust"],
        "cwf_prob": result["cwf_prob"],
        "zd": result.get("zd", 0),
        "pred_class": result.get("pred_class", ""),
        "last_seen": result["timestamp"],
    }
    emoji = {"SAFE": "🟢", "WATCH": "🟡", "THREAT": "🔴"}.get(result["decision"], "⚪")
    log.info(
        f'{emoji} {result["device_id"]:<15} {result["decision"]:<7} | trust={result["trust"]:.3f} | cwf={result["cwf_prob"]:.3f} | {result.get("pred_class","")}'
    )


# ── MQTT ──────────────────────────────────────────────────────────────────────
_mqtt_client = None


import paho.mqtt.client as mqtt


def _setup_mqtt():
    global _mqtt_client
    if "YOUR" in MQTT_HOST:
        log.warning(
            "⚠️  MQTT not configured — skipping (fill MQTT_HOST, MQTT_USER, MQTT_PASSWORD)"
        )
        return
    try:

        c = mqtt.Client(client_id="safenest_server_" + str(int(time.time())))
        c.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        c.tls_set()
        c.on_connect = lambda cl, u, f, rc: log.info(
            "✅ MQTT connected to HiveMQ" if rc == 0 else f"MQTT connect failed rc={rc}"
        )
        c.on_disconnect = lambda cl, u, rc: (
            log.warning(f"MQTT disconnected rc={rc}"),
            time.sleep(5),
            cl.reconnect(),
        )
        c.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        c.loop_start()
        _mqtt_client = c
    except Exception as e:
        log.warning(f"MQTT setup failed: {e}")


def publish_mqtt(result):
    if _mqtt_client is None:
        return
    try:
        _mqtt_client.publish(MQTT_TOPIC, json.dumps(result), qos=1)
    except Exception as e:
        log.error(f"MQTT publish error: {e}")


# ── Telegram ──────────────────────────────────────────────────────────────────
DEVICE_BN = {
    "home_camera": "লিভিং রুম ক্যামেরা",
    "home_router": "হোম রাউটার",
    "home_lock": "স্মার্ট লক",
}
THREAT_BN = {
    "DDoS-SYN_Flood": "SYN বন্যা",
    "DDoS-Slowloris": "Slowloris",
    "DDoS-UDP_Flood": "UDP বন্যা",
    "Recon-PortScan": "পোর্ট স্ক্যান",
    "BruteForce": "ব্রুট-ফোর্স",
    "Spoofing-ARP_Spoofing": "ARP স্পুফিং",
    "BenignTraffic": "স্বাভাবিক",
}


def send_telegram(result):
    if not TELEGRAM_TOKEN or "YOUR" in TELEGRAM_TOKEN:
        return
    if result["decision"] == "SAFE":
        return
    try:
        import urllib.request, urllib.parse

        dev = DEVICE_BN.get(result["device_id"], result["device_id"])
        threat = THREAT_BN.get(
            result.get("pred_class", ""), result.get("pred_class", "")
        )
        trust = result["trust"]
        cwf = result["cwf_prob"]
        if result["decision"] == "THREAT":
            text = f"🚨 বিপদ! {dev}-এ {threat} সনাক্ত!\nট্রাস্ট: {trust:.0%} | CWF: {cwf:.3f}\n✅ এখনই পদক্ষেপ নিন।"
        else:
            text = f"⚠️ {dev}: সন্দেহজনক কার্যকলাপ ({threat})। ট্রাস্ট: {trust:.0%}"
        data = urllib.parse.urlencode(
            {"chat_id": TELEGRAM_CHAT_ID, "text": text}
        ).encode()
        urllib.request.urlopen(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data, timeout=5
        )
        log.info(f'📱 Telegram alert sent → {result["decision"]}')
    except Exception as e:
        log.error(f"Telegram error: {e}")


def fire_and_forget(result):
    """Publish MQTT + send Telegram in background threads so API doesn't slow down."""
    threading.Thread(target=publish_mqtt, args=(result,), daemon=True).start()
    threading.Thread(target=send_telegram, args=(result,), daemon=True).start()


# ── Demo scenario flows ───────────────────────────────────────────────────────
# Maps scenario name → (flow_features, device_id, trav_overrides, device_age)
DEMO_SCENARIOS = {
    "normal_camera": (
        {
            "flow_pkts_per_sec": 150,
            "fwd_pkts_tot": 45,
            "flow_duration": 5.2,
            "flow_SYN_flag_count": 1,
            "flow_ACK_flag_count": 30,
            "fwd_pkts_payload.avg": 512,
        },
        "home_camera",
        {"geo_asn_trust": 0.97, "peer_corr": 0.95},
        30,
    ),
    "owner_abroad": (
        {
            "flow_pkts_per_sec": 1200,
            "fwd_pkts_tot": 180,
            "flow_duration": 1800,
            "fwd_pkts_payload.avg": 1024,
            "flow_ACK_flag_count": 120,
        },
        "home_camera",
        {"geo_asn_trust": 0.88, "peer_corr": 0.90},
        30,
    ),
    "hacker_camera": (
        {
            "flow_pkts_per_sec": 800,
            "fwd_pkts_tot": 120,
            "flow_duration": 30,
            "fwd_pkts_payload.avg": 400,
            "flow_SYN_flag_count": 50,
            "flow_ACK_flag_count": 50,
        },
        "home_camera",
        {"geo_asn_trust": 0.15, "peer_corr": 0.08},
        30,
    ),
    "new_device": (
        {
            "flow_pkts_per_sec": 100,
            "fwd_pkts_tot": 20,
            "fwd_pkts_payload.avg": 300,
            "flow_duration": 2.0,
        },
        "home_camera",
        {"geo_asn_trust": 0.70, "peer_corr": 0.60},
        2,  # device_age < 7 → always WATCH
    ),
    "ddos_router": (
        {
            "flow_pkts_per_sec": 12000,
            "fwd_pkts_tot": 4000,
            "flow_SYN_flag_count": 4000,
            "flow_ACK_flag_count": 0,
            "fwd_pkts_payload.avg": 40,
            "flow_duration": 0.3,
        },
        "home_router",
        {"geo_asn_trust": 0.10, "peer_corr": 0.05},
        30,
    ),
    "brute_force": (
        {
            "flow_pkts_per_sec": 200,
            "fwd_pkts_tot": 80,
            "fwd_pkts_payload.avg": 220,
            "flow_SYN_flag_count": 80,
            "flow_ACK_flag_count": 80,
            "flow_duration": 1.5,
        },
        "home_lock",
        {"geo_asn_trust": 0.12, "peer_corr": 0.08},
        30,
    ),
    "port_scan": (
        {
            "flow_pkts_per_sec": 500,
            "fwd_pkts_tot": 2,
            "bwd_pkts_tot": 0,
            "fwd_pkts_payload.avg": 0,
            "flow_duration": 0.005,
            "flow_SYN_flag_count": 1,
            "flow_RST_flag_count": 1,
        },
        "home_router",
        {"geo_asn_trust": 0.18, "peer_corr": 0.06},
        30,
    ),
    "arp_spoof": (
        {
            "flow_pkts_per_sec": 30,
            "fwd_pkts_tot": 5,
            "fwd_pkts_payload.avg": 42,
            "flow_duration": 0.04,
            "flow_SYN_flag_count": 0,
        },
        "home_router",
        {"geo_asn_trust": 0.10, "peer_corr": 0.04},
        30,
    ),
}

# Maps the 5 dashboard scenario buttons (0-4) to scenario names
DASHBOARD_SCENARIO_MAP = {
    0: "normal_camera",
    1: "owner_abroad",
    2: "hacker_camera",
    3: "new_device",
    4: "ddos_router",
}


# ════════════════════════════════════════════════════════════════
#   FLASK ROUTES
# ════════════════════════════════════════════════════════════════


@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "service": "SafeNest Guard Server",
            "pipeline_loaded": PIPELINE_LOADED,
            "endpoints": {
                "GET  /health": "Server + model status",
                "POST /scenario/<n>": "Run dashboard scenario 0-4 (for scenario buttons)",
                "POST /demo/<name>": "Run named demo scenario",
                "POST /predict": "Run inference on custom flow features",
                "GET  /devices": "Current state of all 3 devices",
                "GET  /log?n=50": "Last N events",
                "POST /reset": "Reset TRAV + event log",
            },
            "scenarios": list(DEMO_SCENARIOS.keys()),
        }
    )


@app.route("/dashboard", methods=["GET"])
def dashboard_page():
    return render_template(
        "safenest_dashboard_v2.html",
        MQTT_HOST=MQTT_HOST,
        MQTT_USER=MQTT_USER,
        MQTT_PASSWORD=MQTT_PASSWORD,
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "ok",
            "pipeline_loaded": PIPELINE_LOADED,
            "model_dir": MODEL_DIR,
            "features": len(FEAT_COLS),
            "classes": list(le.classes_) if PIPELINE_LOADED else [],
            "gru_loaded": gru_model is not None if PIPELINE_LOADED else False,
            "mqtt_configured": "YOUR" not in MQTT_HOST,
            "telegram_configured": "YOUR" not in TELEGRAM_TOKEN,
        }
    )


@app.route("/scenario/<int:n>", methods=["POST"])
def scenario_by_number(n):
    """Called by the dashboard scenario buttons (0–4)."""
    scenario = DASHBOARD_SCENARIO_MAP.get(n)
    if scenario is None:
        return jsonify({"error": f"Scenario {n} not found. Use 0–4."}), 404
    return _run_scenario(scenario)


@app.route("/demo/<scenario_name>", methods=["POST"])
def demo_by_name(scenario_name):
    """Called with a named scenario."""
    return _run_scenario(scenario_name)


def _run_scenario(scenario_name):
    if scenario_name not in DEMO_SCENARIOS:
        return (
            jsonify(
                {
                    "error": f"Unknown scenario: {scenario_name}",
                    "available": list(DEMO_SCENARIOS.keys()),
                }
            ),
            404,
        )

    flow, device_id, trav_ovr, device_age = DEMO_SCENARIOS[scenario_name]
    result = run_inference(
        flow, device_id=device_id, trav_overrides=trav_ovr, device_age=device_age
    )
    result["scenario"] = scenario_name

    save_event(result)
    fire_and_forget(result)

    return jsonify(result)


@app.route("/predict", methods=["POST"])
def predict():
    """Run inference on custom flow features."""
    body = request.get_json(force=True) or {}
    device_id = body.get("device_id", "home_camera")
    features = body.get("features", {})
    trav_ovr = body.get("trav", {})
    age = int(body.get("device_age", 30))

    if device_id not in DEVICE_STATE:
        return jsonify({"error": f"Unknown device: {device_id}"}), 400

    result = run_inference(
        features, device_id=device_id, trav_overrides=trav_ovr, device_age=age
    )
    save_event(result)
    fire_and_forget(result)
    return jsonify(result)


@app.route("/devices", methods=["GET"])
def devices():
    return jsonify({"devices": DEVICE_STATE, "timestamp": time.time()})


@app.route("/log", methods=["GET"])
def event_log():
    n = min(int(request.args.get("n", 50)), 300)
    return jsonify({"events": list(reversed(EVENT_LOG[-n:])), "total": len(EVENT_LOG)})


@app.route("/reset", methods=["POST"])
def reset():
    global EVENT_LOG
    EVENT_LOG = []
    trav.reset()
    for dev in DEVICE_STATE:
        DEVICE_STATE[dev] = {
            "decision": "SAFE",
            "trust": 0.95,
            "cwf_prob": 0.005,
            "zd": 0.07,
            "pred_class": "BenignTraffic",
            "last_seen": time.time(),
        }
        for _ in range(5):
            trav.update(
                dev, {"bw": 1000, "hour": 20, "geo_asn_trust": 0.9, "peer_corr": 0.9}
            )
    log.info("🔄 State reset")
    return jsonify({"status": "reset done"})


# ── Background Pi bridge loop ─────────────────────────────────────────────────
# This simulates the Pi running continuously and publishing to MQTT.
# In production on Pi, replace capture_next_flow() with real CICFlowMeter output.


def capture_next_flow():
    """Synthetic flow for demo — replace with CICFlowMeter CSV rows on real Pi."""
    rng = np.random.RandomState(int(time.time()) % 1000)
    flow = {c: float(rng.exponential(100)) for c in FEAT_COLS} if FEAT_COLS else {}
    flow["flow_pkts_per_sec"] = float(rng.uniform(80, 200))
    flow["fwd_pkts_tot"] = float(rng.randint(20, 80))
    return flow


def pi_bridge_loop():
    """Runs in background — mimics Pi capturing and classifying traffic every 5s."""
    devices_cycle = ["home_camera", "home_router", "home_lock"]
    idx = 0
    time.sleep(3)  # wait for Flask to start
    log.info("🔄 Pi bridge loop started (background)")
    while True:
        try:
            device_id = devices_cycle[idx % len(devices_cycle)]
            idx += 1
            flow = capture_next_flow()
            result = run_inference(flow, device_id=device_id)
            save_event(result)
            publish_mqtt(result)  # push to dashboard live
            # Telegram only for real alerts, not SAFE background traffic
            if result["decision"] != "SAFE":
                threading.Thread(
                    target=send_telegram, args=(result,), daemon=True
                ).start()
        except Exception as e:
            log.error(f"Pi bridge loop error: {e}")
        time.sleep(5)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       SafeNest Guard — Complete Backend Server          ║")
    print(
        f'║  Pipeline: {"✅ LOADED" if PIPELINE_LOADED else "⚠️  DEMO MODE — fix MODEL_DIR"}'
    )
    print(
        f'║  MQTT:     {"✅ configured" if "YOUR" not in MQTT_HOST else "⚠️  not set — fill MQTT_HOST etc"}'
    )
    print(
        f'║  Telegram: {"✅ configured" if "YOUR" not in TELEGRAM_TOKEN else "⚠️  not set — fill TELEGRAM_TOKEN etc"}'
    )
    print("║  API:       http://localhost:5000                       ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("  Open safenest_dashboard_final.html in your browser.")
    print("  Click any scenario button — inference runs, MQTT publishes,")
    print("  Telegram sends, dashboard updates.")
    print()

    _setup_mqtt()

    # Start Pi bridge background thread
    threading.Thread(target=pi_bridge_loop, daemon=True).start()

    app.run(host="0.0.0.0", port=5000, debug=False)
