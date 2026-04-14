"""
safenest_api.py — SafeNest Guard REST API Backend
==================================================
Loads all trained models from safenest_output/ and exposes a Flask API.
Send any network flow as a POST request, get a full prediction back.

USAGE
-----
1. Copy this file + safenest_output/ folder to the same directory on Pi or laptop.
2. Install deps:
       pip install flask scikit-learn xgboost tensorflow joblib scipy
3. Run:
       python safenest_api.py
4. API is live at http://localhost:5000

ENDPOINTS
---------
POST /predict          — run full SafeNestGuard pipeline on one flow
POST /predict/batch    — run on multiple flows at once
GET  /health           — check server is up and models are loaded
GET  /features         — list expected feature names
GET  /devices          — list registered TRAV device profiles
POST /register_session — add a trusted session to TRAV profile
"""

import os, sys, json, time, math, pickle, joblib, logging
import numpy as np
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from scipy.stats import entropy as scipy_entropy

# ── Optional TF import (graceful if not installed) ─────────────────────────
try:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    from tensorflow import keras

    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("safenest")

app = Flask(__name__)
CORS(app)
# ── Configuration ──────────────────────────────────────────────────────────
MODEL_DIR = "./models"

# ══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS  (extracted from notebook Blocks 6, 7, 8, 9, 10)
# ══════════════════════════════════════════════════════════════════════════

HIGH_RISK_PORTS = {23, 2323, 5555, 9090, 8080, 7547, 48101, 37777, 34567, 4786}
DEVICE_TYPES = {
    "camera": 0,
    "lock": 1,
    "router": 2,
    "tv": 3,
    "rfid": 4,
    "sensor": 5,
    "unknown": 6,
}

BANGLA_DEVICE = {
    "camera": "ক্যামেরা",
    "lock": "দরজার লক",
    "router": "রাউটার",
    "tv": "স্মার্ট টিভি",
    "rfid": "আরএফআইডি টার্মিনাল",
    "sensor": "সেন্সর",
    "unknown": "ডিভাইস",
    "home_camera": "বাড়ির ক্যামেরা",
    "home_lock": "দরজার স্মার্ট লক",
    "home_router": "হোম রাউটার",
    "nsu_cam_floor3": "NSU ক্যামেরা (৩য় তলা)",
    "nsu_smart_lock": "NSU স্মার্ট লক",
    "office_cam": "অফিস ক্যামেরা",
}

TMPL_EN = {
    "SAFE": {
        "normal": "Your {device} is working normally. All clear.",
        "trusted_remote": "Your {device} is being accessed remotely by a recognized device. Everything looks fine.",
    },
    "CAUTION": {
        "new_device": "A new device has joined your network. Monitoring started.",
        "signals_disagree": "Something slightly unusual on your {device}. Nothing confirmed yet — keep an eye on it.",
        "suspicious_remote": "Remote connection to your {device} does not match your usual pattern. Is this you?",
    },
    "ALERT": {
        "attack": "Your {device} is showing signs of a cyber attack. Check immediately.",
        "zero_day": "An unusual, possibly new type of threat on your {device}. Disconnect if possible.",
    },
    "REVIEW": {
        "uncertain": "Not fully certain about recent activity on your {device}. A quick check when convenient."
    },
}
TMPL_BN = {
    "SAFE": {
        "normal": "✅ আপনার {device} সম্পূর্ণ স্বাভাবিক ও নিরাপদ।",
        "trusted_remote": "✅ আপনার {device}-এ পরিচিত দূরবর্তী সংযোগ। সবকিছু ঠিক আছে।",
    },
    "CAUTION": {
        "new_device": "⚠️ নতুন ডিভাইস নেটওয়ার্কে যুক্ত হয়েছে। পর্যবেক্ষণ শুরু।",
        "signals_disagree": "⚠️ আপনার {device}-এ সামান্য অস্বাভাবিক কার্যকলাপ। এখনই বিপদ নয়, নজর রাখুন।",
        "suspicious_remote": "⚠️ {device}-এ দূরবর্তী সংযোগ যা পরিচিত প্যাটার্নের সাথে মেলে না।",
    },
    "ALERT": {
        "attack": "🚨 সতর্কতা! আপনার {device}-এ সাইবার আক্রমণের লক্ষণ। এখনই পদক্ষেপ নিন।",
        "zero_day": "🚨 অজানা হুমকি! {device}-এ নতুন ধরনের আক্রমণ। সম্ভব হলে বন্ধ করুন।",
    },
    "REVIEW": {
        "uncertain": "🔍 {device}-এর কার্যকলাপ নিয়ে নিশ্চিত নই। সুবিধামতো পরীক্ষা করুন।"
    },
}


def extract_context_vector(
    hour,
    bandwidth_kbps,
    duration_sec,
    dst_port,
    src_country,
    device_type,
    rolling_similarity,
    home_country="BD",
):
    hour_sin = math.sin(2 * math.pi * hour / 24)
    hour_cos = math.cos(2 * math.pi * hour / 24)
    bw_norm = min(1.0, math.log1p(bandwidth_kbps) / math.log1p(10000))
    dur_norm = min(1.0, math.log1p(duration_sec) / math.log1p(3600))
    port_risk = 1.0 if int(dst_port) in HIGH_RISK_PORTS else 0.0
    country_m = 1.0 if src_country == home_country else 0.0
    dev_enc = DEVICE_TYPES.get(str(device_type), DEVICE_TYPES["unknown"])
    dev_norm = dev_enc / max(DEVICE_TYPES.values())
    return np.array(
        [
            hour_sin,
            hour_cos,
            bw_norm,
            dur_norm,
            port_risk,
            country_m,
            dev_norm,
            float(rolling_similarity),
        ],
        dtype=np.float32,
    )


def get_entropy(p):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return float(scipy_entropy([1 - p, p]))


def decide(
    fused_score,
    conflict,
    is_zero_day,
    entropy,
    trav_trusted,
    trav_score,
    device_status,
    entropy_threshold,
):
    if device_status == "UNREGISTERED":
        return (
            "CAUTION",
            "New unregistered device detected on network. Profile being built.",
            0.45,
        )
    if trav_trusted and trav_score >= 0.68:
        return (
            "SAFE",
            f"Known owner remote access recognized (TRAV={trav_score:.2f}).",
            fused_score * 0.10,
        )
    if is_zero_day and fused_score > 0.75:
        return (
            "ALERT",
            f"Possible zero-day attack — supervised models flag new type "
            f"(conflict={conflict:.2f}). Isolate device.",
            min(fused_score * 1.3, 1.0),
        )
    if entropy > entropy_threshold or conflict > 0.55:
        return (
            "REVIEW",
            f"Signals uncertain (entropy={entropy:.3f}, conflict={conflict:.2f}). "
            f"Manual check recommended.",
            fused_score,
        )
    if fused_score >= 0.78:
        return (
            "ALERT",
            f"High-confidence attack (score={fused_score:.2f}).",
            fused_score,
        )
    if fused_score >= 0.45:
        return ("CAUTION", f"Unusual traffic (score={fused_score:.2f}).", fused_score)
    return ("SAFE", f"Normal traffic (score={fused_score:.2f}).", fused_score)


def _alert_key(decision, reason_en, device_status, trav_trusted, is_zero_day):
    if decision == "SAFE":
        return "trusted_remote" if trav_trusted else "normal"
    if decision == "CAUTION":
        if device_status == "UNREGISTERED":
            return "new_device"
        if "remote" in reason_en.lower() or "suspicious" in reason_en.lower():
            return "suspicious_remote"
        return "signals_disagree"
    if decision == "ALERT":
        return "zero_day" if is_zero_day else "attack"
    return "uncertain"


def build_alert(
    decision,
    reason_en,
    device_id,
    device_type="unknown",
    is_zero_day=False,
    trav_trusted=False,
    device_status="REGISTERED",
):
    dev_en = device_id.replace("_", " ").title()
    dev_bn = BANGLA_DEVICE.get(
        device_id, BANGLA_DEVICE.get(device_type, BANGLA_DEVICE["unknown"])
    )
    key = _alert_key(decision, reason_en, device_status, trav_trusted, is_zero_day)
    en = (
        TMPL_EN[decision]
        .get(key, list(TMPL_EN[decision].values())[0])
        .format(device=dev_en)
    )
    bn = (
        TMPL_BN[decision]
        .get(key, list(TMPL_BN[decision].values())[0])
        .format(device=dev_bn)
    )
    return en, bn


# ══════════════════════════════════════════════════════════════════════════
# MODEL CLASSES (extracted from notebook Blocks 4, 7, 8)
# ══════════════════════════════════════════════════════════════════════════


class NewDeviceHandler:
    N_BOOTSTRAP = 50

    def __init__(self):
        self.devices = {}

    def see_device(self, device_id, flow_features, if_score):
        if device_id not in self.devices:
            self.devices[device_id] = {
                "flows": [],
                "status": "UNREGISTERED",
                "first_seen": time.time(),
            }
        dev = self.devices[device_id]
        dev["flows"].append(np.array(flow_features))
        if dev["status"] == "UNREGISTERED":
            n = len(dev["flows"])
            if n >= self.N_BOOTSTRAP:
                dev["status"] = "REGISTERED"
                return (
                    "REGISTERED",
                    float(if_score),
                    f"{device_id} promoted after {n} flows.",
                )
            return (
                "UNREGISTERED",
                min(float(if_score) * 1.2, 1.0),
                f"New device — profile building ({n}/{self.N_BOOTSTRAP})",
            )
        return "REGISTERED", float(if_score), None


class ContextWeightedFusion:
    SIGNAL_NAMES = ["rf", "xgb", "if_ae", "trav"]

    def __init__(self):
        self.weight_models = []
        self.is_fitted = False

    def _generate_training_data(self, n=8000):
        from sklearn.linear_model import LogisticRegression

        rng = np.random.RandomState(99)
        ctx = rng.rand(n, 8).astype(np.float32)
        targets = np.zeros((n, 4), dtype=np.float32)
        for i in range(n):
            bw_norm, port_risk = ctx[i, 2], ctx[i, 4]
            country_m, rolling = ctx[i, 5], ctx[i, 7]
            w_rf = 0.25 + 0.20 * bw_norm + 0.10 * (1 - country_m)
            w_xgb = 0.25 + 0.15 * bw_norm + 0.10 * (1 - country_m)
            w_ifae = 0.20 + 0.25 * port_risk
            w_trav = 0.15 + 0.30 * rolling * country_m
            total = w_rf + w_xgb + w_ifae + w_trav
            targets[i] = [w_rf / total, w_xgb / total, w_ifae / total, w_trav / total]
        return ctx, targets

    def fit(self):
        from sklearn.linear_model import LogisticRegression

        ctx, targets = self._generate_training_data()
        self.weight_models = []
        for k in range(4):
            y_k = (targets[:, k] > targets[:, k].mean()).astype(int)
            lr = LogisticRegression(max_iter=500, random_state=42)
            lr.fit(ctx, y_k)
            self.weight_models.append(lr)
        self.is_fitted = True

    def get_weights(self, ctx_vec):
        ctx = ctx_vec.reshape(1, -1)
        raw = np.array([m.predict_proba(ctx)[0, 1] for m in self.weight_models])
        return raw / (raw.sum() + 1e-9)

    def fuse(self, prob_rf, prob_xgb, zd_score, trav_score, ctx_vec):
        if not self.is_fitted:
            raise RuntimeError("CWF not fitted.")
        trav_risk = 1.0 - trav_score
        signals = np.array([prob_rf, prob_xgb, zd_score, trav_risk])
        weights = self.get_weights(ctx_vec)
        fused = float(np.dot(weights, signals))
        pairs = [
            (signals[i], signals[j])
            for i in range(len(signals))
            for j in range(i + 1, len(signals))
        ]
        conflict = float(np.mean([abs(a - b) for a, b in pairs]))
        sup_avg = (prob_rf + prob_xgb) / 2
        unsup_avg = (zd_score + trav_risk) / 2
        is_zero_day = bool(sup_avg > 0.65 and unsup_avg < 0.35)
        if is_zero_day:
            fused = max(fused, sup_avg * 0.90)
        return {
            "fused_score": round(fused, 4),
            "conflict": round(conflict, 4),
            "weights": {
                k: round(float(v), 3) for k, v in zip(self.SIGNAL_NAMES, weights)
            },
            "is_zero_day": is_zero_day,
        }


class TRAVEngine:
    TRUST_THRESHOLD = 0.68
    HISTORY_SIZE = 7

    def __init__(self):
        self.profiles = {}
        self.history = {}

    def register_session(self, device_id, hour, bw_kbps, dur_sec, country):
        if device_id not in self.profiles:
            self.profiles[device_id] = []
            self.history[device_id] = []
        session = {"hour": hour, "bw": bw_kbps, "dur": dur_sec, "country": country}
        self.profiles[device_id].append(session)
        self.history[device_id].append(session)
        if len(self.history[device_id]) > self.HISTORY_SIZE:
            self.history[device_id].pop(0)

    def get_trav_score(self, device_id, hour, bw_kbps, dur_sec, country):
        if device_id not in self.history or len(self.history[device_id]) < 2:
            return 0.5
        scores = []
        for s in self.history[device_id]:
            h_dist = min(abs(hour - s["hour"]), 24 - abs(hour - s["hour"]))
            h_sim = 1.0 - h_dist / 12.0
            b_sim = max(0.0, 1.0 - abs(bw_kbps - s["bw"]) / (max(s["bw"], 100)))
            d_sim = max(0.0, 1.0 - abs(dur_sec - s["dur"]) / (max(s["dur"], 30)))
            c_sim = 1.0 if country == s["country"] else 0.3
            scores.append(h_sim * 0.30 + b_sim * 0.35 + d_sim * 0.25 + c_sim * 0.10)
        final = float(np.mean(scores))
        if 1000 < bw_kbps < 4500 and 60 < dur_sec < 1800:
            final = min(1.0, final * 1.35)
        return round(final, 3)

    def is_trusted(self, device_id, hour, bw_kbps, dur_sec, country):
        score = self.get_trav_score(device_id, hour, bw_kbps, dur_sec, country)
        return score >= self.TRUST_THRESHOLD, score


# ══════════════════════════════════════════════════════════════════════════
# SAFENEST GUARD — INFERENCE ENGINE
# ══════════════════════════════════════════════════════════════════════════


class SafeNestGuard:
    """
    Full inference pipeline. Loads all saved models from MODEL_DIR.
    One instance is created at server startup and reused for every request.
    """

    def __init__(self):
        self.rf = None
        self.xgb_m = None
        self.ae = None
        self.if_model = None
        self.scaler = None
        self.calib_rf = None
        self.calib_xgb = None
        self.trav = None
        self.cwf = None
        self.feature_names = []
        self.ae_threshold = 0.5
        self.entropy_thresh = 0.5
        self.if_min = 0.0
        self.if_max = 1.0
        self.ndh = NewDeviceHandler()
        self.ready = False

    def load(self, model_dir):
        log.info(f"Loading models from {model_dir} ...")
        t0 = time.time()

        self.rf = joblib.load(f"{model_dir}/model_rf.pkl")
        self.xgb_m = joblib.load(f"{model_dir}/model_xgb.pkl")
        self.if_model = joblib.load(f"{model_dir}/model_if.pkl")
        self.scaler = joblib.load(f"{model_dir}/scaler.pkl")
        self.calib_rf = joblib.load(f"{model_dir}/calibrator_rf.pkl")
        self.calib_xgb = joblib.load(f"{model_dir}/calibrator_xgb.pkl")

        with open(f"{model_dir}/trav_engine.pkl", "rb") as f:
            self.trav = pickle.load(f)
        with open(f"{model_dir}/cwf_model.pkl", "rb") as f:
            self.cwf = pickle.load(f)

        with open(f"{model_dir}/feature_names.json") as f:
            self.feature_names = json.load(f)
        with open(f"{model_dir}/ae_threshold.json") as f:
            self.ae_threshold = json.load(f)["threshold"]
        with open(f"{model_dir}/entropy_threshold.json") as f:
            self.entropy_thresh = json.load(f)["threshold"]
        with open(f"{model_dir}/if_norm_bounds.json") as f:
            b = json.load(f)
            self.if_min = b["if_min"]
            self.if_max = b["if_max"]

        # Load Autoencoder (optional — falls back to IF-only zero-day)
        if TF_AVAILABLE:
            ae_path = f"{model_dir}/autoencoder.keras"
            tflite = f"{model_dir}/autoencoder.tflite"
            if os.path.exists(ae_path):
                self.ae = keras.models.load_model(ae_path)
                log.info("Autoencoder loaded (keras)")
            elif os.path.exists(tflite):
                import tensorflow as tf

                self.ae_tflite = tf.lite.Interpreter(model_path=tflite)
                self.ae_tflite.allocate_tensors()
                self.ae = "tflite"
                log.info("Autoencoder loaded (TFLite)")

        self.ready = True
        log.info(
            f"All models loaded in {time.time()-t0:.1f}s. "
            f"Features: {len(self.feature_names)}"
        )
        return self

    def _preprocess(self, flow: dict) -> np.ndarray:
        vec = np.array(
            [float(flow.get(f, 0.0)) for f in self.feature_names], dtype=np.float32
        )
        vec = np.nan_to_num(vec, nan=0.0, posinf=0.0, neginf=0.0)
        return np.clip(self.scaler.transform(vec.reshape(1, -1)), -10, 10)

    def _ae_score(self, X: np.ndarray) -> float:
        if self.ae is None:
            return 0.5  # no AE — neutral
        if self.ae == "tflite":
            inp = self.ae_tflite.get_input_details()
            out = self.ae_tflite.get_output_details()
            self.ae_tflite.set_tensor(inp[0]["index"], X.astype(np.float32))
            self.ae_tflite.invoke()
            recon = self.ae_tflite.get_tensor(out[0]["index"])
        else:
            recon = self.ae.predict(X, verbose=0)
        err = float(np.mean((X - recon) ** 2))
        return float(np.clip(err / (self.ae_threshold * 2), 0, 1))

    def predict(
        self,
        flow: dict,
        device_id: str,
        hour: int = 12,
        bw_kbps: float = 500,
        dur_sec: float = 60,
        country: str = "BD",
        device_type: str = "unknown",
        dst_port: int = 80,
    ) -> dict:

        if not self.ready:
            raise RuntimeError("Models not loaded. Call .load() first.")

        t0 = time.time()
        X = self._preprocess(flow)

        # Supervised (calibrated)
        p_rf = float(self.calib_rf.predict([self.rf.predict_proba(X)[0, 1]])[0])
        p_xgb = float(self.calib_xgb.predict([self.xgb_m.predict_proba(X)[0, 1]])[0])

        # IF (normalized using training bounds — consistent on Pi)
        if_raw = float(-self.if_model.score_samples(X)[0])
        if_score = float(
            np.clip((if_raw - self.if_min) / (self.if_max - self.if_min + 1e-9), 0, 1)
        )

        # AE zero-day
        ae_s = self._ae_score(X)
        zd_score = float(np.sqrt(if_score * ae_s))

        # TRAV
        trav_score = self.trav.get_trav_score(
            device_id, hour, bw_kbps, dur_sec, country
        )
        trav_trusted, _ = self.trav.is_trusted(
            device_id, hour, bw_kbps, dur_sec, country
        )

        # Context vector
        ctx = extract_context_vector(
            hour, bw_kbps, dur_sec, dst_port, country, device_type, trav_score
        )

        # CWF fusion
        fusion = self.cwf.fuse(p_rf, p_xgb, zd_score, trav_score, ctx)

        # Entropy
        ent = get_entropy((p_rf + p_xgb) / 2)

        # New device check
        ndh_status, _, _ = self.ndh.see_device(device_id, X[0], if_score)

        # Decision
        decision, reason_en, severity = decide(
            fusion["fused_score"],
            fusion["conflict"],
            fusion["is_zero_day"],
            ent,
            trav_trusted,
            trav_score,
            ndh_status,
            self.entropy_thresh,
        )

        # Alerts
        alert_en, alert_bn = build_alert(
            decision,
            reason_en,
            device_id,
            device_type,
            fusion["is_zero_day"],
            trav_trusted,
            ndh_status,
        )

        return {
            "device_id": device_id,
            "decision": decision,
            "severity": round(severity, 3),
            "alert_en": alert_en,
            "alert_bn": alert_bn,
            "reason": reason_en,
            "scores": {
                "rf": round(p_rf, 4),
                "xgb": round(p_xgb, 4),
                "if": round(if_score, 4),
                "ae": round(ae_s, 4),
                "zd": round(zd_score, 4),
                "trav": round(trav_score, 4),
                "fused": fusion["fused_score"],
            },
            "meta": {
                "conflict": fusion["conflict"],
                "is_zero_day": fusion["is_zero_day"],
                "signal_weights": fusion["weights"],
                "entropy": round(ent, 4),
                "trav_trusted": trav_trusted,
                "device_status": ndh_status,
                "latency_ms": round((time.time() - t0) * 1000, 1),
            },
        }


# ══════════════════════════════════════════════════════════════════════════
# STARTUP — load models once
# ══════════════════════════════════════════════════════════════════════════

guard = SafeNestGuard()

# ── Dashboard result store ─────────────────────────────────────────────────
import threading as _th

_lock = _th.Lock()
_results = {
    "showcase": [],  # last 5 showcase results
    "random": [],  # last 50 random results
    "stream": [],  # last 100 any results (all predictions)
    "counts": {"SAFE": 0, "CAUTION": 0, "ALERT": 0, "REVIEW": 0},
    "latencies": [],
    "zero_days": 0,
    "trav_trusted": 0,
    "total": 0,
}
_stream_id = 0


def _record(result, label="", src="", bw=0, country=""):
    """Record a prediction result to the dashboard store."""
    global _stream_id
    with _lock:
        dec = result.get("decision", "REVIEW")
        lat = result.get("meta", {}).get("latency_ms", 0)
        zd = result.get("meta", {}).get("is_zero_day", False)
        tt = result.get("meta", {}).get("trav_trusted", False)
        import time as _t

        r = dict(result)
        _stream_id += 1
        r["_id"] = _stream_id
        r["_label"] = label
        r["_src"] = src
        r["_bw"] = bw
        r["_country"] = country
        r["timestamp"] = _t.time()
        _results["counts"][dec] = _results["counts"].get(dec, 0) + 1
        _results["latencies"].append(lat)
        if len(_results["latencies"]) > 100:
            _results["latencies"] = _results["latencies"][-100:]
        if zd:
            _results["zero_days"] += 1
        if tt:
            _results["trav_trusted"] += 1
        _results["total"] += 1
        _results["stream"].append(r)
        if len(_results["stream"]) > 100:
            _results["stream"] = _results["stream"][-100:]


def startup():
    if not os.path.isdir(MODEL_DIR):
        log.error(f"Model directory not found: {MODEL_DIR}")
        log.error("Set SAFENEST_MODEL_DIR env variable or place safenest_output/ here.")
        sys.exit(1)
    guard.load(MODEL_DIR)


# ══════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

@app.route("/health", methods=["GET"])
def health():
    """Quick health check."""
    return jsonify(
        {
            "status": "ok" if guard.ready else "loading",
            "model_dir": MODEL_DIR,
            "feature_count": len(guard.feature_names),
            "trav_devices": list(guard.trav.profiles.keys()) if guard.trav else [],
            "autoencoder": str(guard.ae is not None),
        }
    )


@app.route("/features", methods=["GET"])
def features():
    """Return the list of expected feature names for flow dicts."""
    return jsonify(
        {
            "count": len(guard.feature_names),
            "features": guard.feature_names,
        }
    )


@app.route("/devices", methods=["GET"])
def devices():
    """Return all registered TRAV device profiles."""
    if not guard.trav:
        return jsonify({"error": "TRAV not loaded"}), 500
    profiles = {}
    for dev_id, sessions in guard.trav.profiles.items():
        profiles[dev_id] = {
            "session_count": len(sessions),
            "history": guard.trav.history.get(dev_id, []),
        }
    return jsonify(profiles)


@app.route("/register_session", methods=["POST"])
def register_session():
    """
    Add a confirmed-legitimate session to TRAV profile.
    Body: { device_id, hour, bw_kbps, dur_sec, country }
    """
    body = request.get_json(force=True)
    required = ["device_id", "hour", "bw_kbps", "dur_sec", "country"]
    missing = [k for k in required if k not in body]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    guard.trav.register_session(
        body["device_id"],
        int(body["hour"]),
        float(body["bw_kbps"]),
        float(body["dur_sec"]),
        str(body["country"]),
    )
    return jsonify(
        {
            "ok": True,
            "device_id": body["device_id"],
            "session_count": len(guard.trav.profiles.get(body["device_id"], [])),
        }
    )


@app.route("/register_device", methods=["POST"])
def register_device():
    """
    Pre-register a device as REGISTERED in the NewDeviceHandler.
    Call this BEFORE sending predict requests for known devices.
    Without this, every device starts as UNREGISTERED and returns
    CAUTION regardless of what the ML models say.

    Body: { "device_id": "home_camera" }
          OR { "device_ids": ["home_camera", "home_lock", "home_router"] }
    """
    body = request.get_json(force=True)

    # Accept single or list
    if "device_ids" in body:
        ids = body["device_ids"]
    elif "device_id" in body:
        ids = [body["device_id"]]
    else:
        return jsonify({"error": "Send 'device_id' or 'device_ids'"}), 400

    registered = []
    for dev_id in ids:
        dev_id = str(dev_id)
        # Force status to REGISTERED directly
        guard.ndh.devices[dev_id] = {
            "flows": [],
            "status": "REGISTERED",
            "first_seen": time.time(),
        }
        registered.append(dev_id)

    log.info(f"Pre-registered devices: {registered}")
    return jsonify({"ok": True, "registered": registered})


@app.route("/reset_devices", methods=["POST"])
def reset_devices():
    """
    Reset the NewDeviceHandler — all devices go back to UNREGISTERED.
    Useful for demo resets between showcase runs.
    """
    guard.ndh.devices = {}
    return jsonify({"ok": True, "message": "All device profiles cleared."})


# ── Serve dashboard HTML ───────────────────────────────────────────────────
@app.route("/", methods=["GET"])
@app.route("/dashboard", methods=["GET"])
def dashboard_page():
    """Serve the dashboard HTML."""
    import os as _os

    html_path = _os.path.join(
        _os.path.dirname(_os.path.abspath(__file__)), "safenest_dashboard.html"
    )
    if not _os.path.exists(html_path):
        return (
            '<h2 style="font-family:monospace;padding:40px;color:#ff3b5c">'
            "safenest_dashboard.html not found.<br>"
            "Place it in the same folder as safenest_api.py</h2>"
        ), 404
    with open(html_path, encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/dashboard_data", methods=["GET"])
def dashboard_data():
    """Return all recorded results for the dashboard to poll."""
    with _lock:
        lats = _results["latencies"]
        stats = {
            "total": _results["total"],
            "avg_latency": round(sum(lats) / len(lats), 1) if lats else 0,
            "min_latency": round(min(lats), 1) if lats else 0,
            "max_latency": round(max(lats), 1) if lats else 0,
            "zero_days": _results["zero_days"],
            "trav_trusted": _results["trav_trusted"],
        }
        return jsonify(
            {
                "counts": dict(_results["counts"]),
                "stats": stats,
                "recent_latencies": lats[-20:],
                "showcase": list(_results["showcase"]),
                "random": list(_results["random"]),
                "stream": list(_results["stream"]),
            }
        )


@app.route("/dashboard/reset", methods=["POST"])
def dashboard_reset():
    """Clear all recorded results."""
    global _stream_id
    with _lock:
        _results["showcase"].clear()
        _results["random"].clear()
        _results["stream"].clear()
        _results["counts"] = {"SAFE": 0, "CAUTION": 0, "ALERT": 0, "REVIEW": 0}
        _results["latencies"] = []
        _results["zero_days"] = 0
        _results["trav_trusted"] = 0
        _results["total"] = 0
        _stream_id = 0
    return jsonify({"ok": True})


@app.route("/dashboard/add_showcase", methods=["POST"])
def add_showcase():
    """
    Test client calls this after each showcase scenario run.
    Body: same as predict response, plus optional _label field.
    """
    body = request.get_json(force=True)
    with _lock:
        _results["showcase"].append(body)
        if len(_results["showcase"]) > 10:
            _results["showcase"] = _results["showcase"][-10:]
    _record(body, label=body.get("_label", "showcase"))
    return jsonify({"ok": True})


@app.route("/dashboard/add_random", methods=["POST"])
def add_random():
    """Test client calls this after each random flow."""
    body = request.get_json(force=True)
    with _lock:
        _results["random"].append(body)
        if len(_results["random"]) > 100:
            _results["random"] = _results["random"][-100:]
    _record(
        body,
        label=body.get("_label", "random"),
        src=body.get("_src", ""),
        bw=body.get("_bw", 0),
        country=body.get("_country", ""),
    )
    return jsonify({"ok": True})


@app.route("/predict", methods=["POST"])
def predict():
    """
    Run full SafeNestGuard pipeline on a single flow.

    Required body fields:
        flow        : dict  — network flow features (keys = feature names)
        device_id   : str   — e.g. 'home_camera'

    Optional body fields (session context — important for TRAV):
        hour        : int   — 0-23, current hour. Default 12.
        bw_kbps     : float — session bandwidth in kbps. Default 500.
        dur_sec     : float — session duration in seconds. Default 60.
        country     : str   — 2-letter country code. Default 'BD'.
        device_type : str   — 'camera'|'lock'|'router'|'tv'|'rfid'|'sensor'|'unknown'
        dst_port    : int   — destination port. Default 80.

    Returns:
        decision    : SAFE | CAUTION | ALERT | REVIEW
        severity    : float [0,1]
        alert_en    : natural language English alert
        alert_bn    : Bangla alert
        scores      : dict of all signal scores
        meta        : conflict, zero_day flag, weights, entropy, latency
    """
    body = request.get_json(force=True)

    if "flow" not in body:
        return (
            jsonify(
                {
                    "error": "'flow' field required. Send network flow features as a dict."
                }
            ),
            400,
        )
    if "device_id" not in body:
        return jsonify({"error": "'device_id' field required. E.g. 'home_camera'"}), 400

    try:
        result = guard.predict(
            flow=body["flow"],
            device_id=str(body["device_id"]),
            hour=int(body.get("hour", 12)),
            bw_kbps=float(body.get("bw_kbps", 500)),
            dur_sec=float(body.get("dur_sec", 60)),
            country=str(body.get("country", "BD")),
            device_type=str(body.get("device_type", "unknown")),
            dst_port=int(body.get("dst_port", 80)),
        )
        _record(result)  # auto-record every prediction to stream
        return jsonify(result)
    except Exception as e:
        log.exception("Prediction error")
        return jsonify({"error": str(e)}), 500


@app.route("/predict/batch", methods=["POST"])
def predict_batch():
    """
    Run predictions on multiple flows at once.

    Body: { "requests": [ {flow, device_id, hour, ...}, ... ] }
    Returns: { "results": [ {...}, ... ] }
    """
    body = request.get_json(force=True)
    if "requests" not in body or not isinstance(body["requests"], list):
        return (
            jsonify({"error": "'requests' must be a list of prediction requests"}),
            400,
        )

    results = []
    for i, req in enumerate(body["requests"]):
        if "flow" not in req or "device_id" not in req:
            results.append({"index": i, "error": "Missing flow or device_id"})
            continue
        try:
            r = guard.predict(
                flow=req["flow"],
                device_id=str(req["device_id"]),
                hour=int(req.get("hour", 12)),
                bw_kbps=float(req.get("bw_kbps", 500)),
                dur_sec=float(req.get("dur_sec", 60)),
                country=str(req.get("country", "BD")),
                device_type=str(req.get("device_type", "unknown")),
                dst_port=int(req.get("dst_port", 80)),
            )
            r["index"] = i
            results.append(r)
        except Exception as e:
            results.append({"index": i, "error": str(e)})

    return jsonify({"results": results, "total": len(results)})


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    startup()
    print("\n" + "=" * 60)
    print("SafeNest Guard API — Running")
    print("=" * 60)
    print(f"Model dir  : {MODEL_DIR}")
    print(f"Features   : {len(guard.feature_names)}")
    print(f"TRAV devices: {list(guard.trav.profiles.keys())}")
    print()
    print("Endpoints:")
    print("  GET  /health              — server status")
    print("  GET  /features            — list of 46 feature names")
    print("  GET  /devices             — TRAV profiles")
    print("  POST /register_session    — add owner session to TRAV")
    print(
        "  POST /register_device     — pre-register device (prevents UNREGISTERED CAUTION)"
    )
    print("  POST /reset_devices       — reset all device profiles for demo")
    print("  POST /predict             — predict one flow")
    print("  POST /predict/batch       — predict multiple flows")
    print()
    print("Dashboard: http://localhost:5000")
    print("Test with:  python safenest_test_client.py")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
