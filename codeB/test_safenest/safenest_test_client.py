"""
safenest_test_client.py — Test Client for SafeNest Guard API
=============================================================
Loads real rows from CICIoT2023.csv and fires them at the Flask backend.
Runs the exact 5 showcase scenarios + random sampling.

USAGE
-----
1. Start the API first:   python safenest_api.py
2. Then in another terminal:
       python safenest_test_client.py

   With a specific dataset path:
       python safenest_test_client.py --dataset /path/to/CICIoT2023.csv

   With a custom API URL (e.g. Pi on your network):
       python safenest_test_client.py --url http://192.168.1.105:5000

   Run only showcase scenarios (no random sampling):
       python safenest_test_client.py --showcase-only

   Run N random samples:
       python safenest_test_client.py --random 20
"""

import argparse
import json
import os
import sys
import time
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import requests

# ── Default config ──────────────────────────────────────────────────────────
DEFAULT_API_URL   = 'http://localhost:5000'
DEFAULT_DATASET   = './dataset/safenest_test_balanced.csv'
LABEL_COL         = 'label'
BENIGN_VAL        = 'BenignTraffic'

# ── Console colors ──────────────────────────────────────────────────────────
GREEN  = '\033[92m'
YELLOW = '\033[93m'
RED    = '\033[91m'
GREY   = '\033[90m'
BOLD   = '\033[1m'
RESET  = '\033[0m'

DECISION_COLORS = {
    'SAFE'   : GREEN,
    'CAUTION': YELLOW,
    'ALERT'  : RED,
    'REVIEW' : GREY,
}
DECISION_ICONS = {
    'SAFE':'✅', 'CAUTION':'⚠️ ', 'ALERT':'🚨', 'REVIEW':'🔍'
}


def color(text, dec):
    return f'{DECISION_COLORS.get(dec, "")}{text}{RESET}'


def separator(char='─', width=70):
    print(char * width)


# ══════════════════════════════════════════════════════════════════════════
# DATASET LOADER
# ══════════════════════════════════════════════════════════════════════════

class DatasetLoader:
    """Loads CICIoT2023 rows and converts them to flow dicts for the API."""

    def __init__(self, csv_path: str, feature_names: list):
        self.csv_path      = csv_path
        self.feature_names = feature_names
        self.df            = None
        self.benign_rows   = None
        self.attack_rows   = {}   # attack_type -> DataFrame

    def load(self, nrows: int = 100_000):
        try:
            import pandas as pd
        except ImportError:
            print('pandas not installed. pip install pandas')
            sys.exit(1)

        print(f'Loading dataset: {self.csv_path} (up to {nrows:,} rows) ...')
        # If using the balanced dataset, load all rows (it's already small)
        actual_nrows = None if 'balanced' in self.csv_path else nrows
        df = pd.read_csv(self.csv_path, nrows=actual_nrows, low_memory=False,
                         on_bad_lines='skip')

        # Fix column names
        df.columns = (df.columns
                      .str.strip()
                      .str.replace(' ', '_', regex=False)
                      .str.replace('/', '_', regex=False)
                      .str.replace('-', '_', regex=False))

        # Ensure all feature columns exist
        for f in self.feature_names:
            if f not in df.columns:
                df[f] = 0.0

        # Numeric conversion
        for f in self.feature_names:
            df[f] = pd.to_numeric(df[f], errors='coerce').fillna(0.0)

        label_col = LABEL_COL
        if label_col not in df.columns:
            # Try to find it
            candidates = [c for c in df.columns if c.lower() in ['label','class','category','attack']]
            label_col  = candidates[0] if candidates else None

        self.df = df
        if label_col:
            df['_label'] = df[label_col].astype(str).str.strip()
            self.benign_rows = df[df['_label'] == BENIGN_VAL].copy()
            attack_df = df[df['_label'] != BENIGN_VAL].copy()
            for atype in attack_df['_label'].unique():
                self.attack_rows[atype] = attack_df[attack_df['_label'] == atype].copy()
            print(f'  Benign rows    : {len(self.benign_rows):,}')
            print(f'  Attack types   : {len(self.attack_rows)}')
            for atype, adf in sorted(self.attack_rows.items(), key=lambda x: -len(x[1]))[:8]:
                print(f'    {atype:<40} {len(adf):>6,}')
            if len(self.attack_rows) > 8:
                print(f'    ... and {len(self.attack_rows)-8} more')
        else:
            print('  Warning: could not find label column. Using all rows as benign.')
            self.benign_rows = df.copy()
        print()

    def sample_row(self, label: str = 'benign', attack_type: str = None) -> dict:
        """Return one random row as a feature dict ready for the API."""
        if label == 'benign':
            src = self.benign_rows
        elif attack_type and attack_type in self.attack_rows:
            src = self.attack_rows[attack_type]
        else:
            all_attack = self.df[self.df.get('_label', self.df.columns[0]) != BENIGN_VAL]
            src = all_attack if len(all_attack) > 0 else self.benign_rows

        row = src.sample(1).iloc[0]
        return {f: float(row.get(f, 0.0)) for f in self.feature_names}

    def random_attack_type(self) -> str:
        if not self.attack_rows:
            return None
        return np.random.choice(list(self.attack_rows.keys()))


# ══════════════════════════════════════════════════════════════════════════
# API CLIENT
# ══════════════════════════════════════════════════════════════════════════

class SafeNestClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def health(self) -> dict:
        return requests.get(f'{self.base_url}/health', timeout=5).json()

    def get_features(self) -> list:
        return requests.get(f'{self.base_url}/features', timeout=5).json()['features']

    def get_devices(self) -> dict:
        return requests.get(f'{self.base_url}/devices', timeout=5).json()

    def register_session(self, device_id, hour, bw_kbps, dur_sec, country) -> dict:
        return requests.post(
            f'{self.base_url}/register_session',
            json={'device_id': device_id, 'hour': hour,
                  'bw_kbps': bw_kbps, 'dur_sec': dur_sec, 'country': country},
            timeout=10
        ).json()

    def predict(self, flow: dict, device_id: str, **kwargs) -> dict:
        payload = {'flow': flow, 'device_id': device_id, **kwargs}
        r = requests.post(f'{self.base_url}/predict', json=payload, timeout=15)
        r.raise_for_status()
        return r.json()

    def register_device(self, device_ids: list) -> dict:
        return requests.post(
            f'{self.base_url}/register_device',
            json={'device_ids': device_ids},
            timeout=10
        ).json()

    def post_showcase(self, result: dict, label: str = '') -> None:
        """Send showcase result to dashboard."""
        try:
            r = dict(result); r['_label'] = label
            requests.post(f'{self.base_url}/dashboard/add_showcase',
                          json=r, timeout=5)
        except Exception:
            pass

    def post_random(self, result: dict, src='', bw=0, country='') -> None:
        """Send random result to dashboard."""
        try:
            r = dict(result)
            r['_src'] = src; r['_bw'] = bw; r['_country'] = country
            requests.post(f'{self.base_url}/dashboard/add_random',
                          json=r, timeout=5)
        except Exception:
            pass

    def reset_dashboard(self) -> None:
        try:
            requests.post(f'{self.base_url}/dashboard/reset', timeout=5)
        except Exception:
            pass

    def reset_devices(self) -> dict:
        return requests.post(
            f'{self.base_url}/reset_devices',
            timeout=10
        ).json()

    def predict_batch(self, requests_list: list) -> dict:
        r = requests.post(
            f'{self.base_url}/predict/batch',
            json={'requests': requests_list},
            timeout=30
        )
        r.raise_for_status()
        return r.json()


# ══════════════════════════════════════════════════════════════════════════
# DISPLAY
# ══════════════════════════════════════════════════════════════════════════

def print_result(result: dict, scenario_name: str = '', show_scores: bool = True):
    dec  = result.get('decision', 'UNKNOWN')
    sev  = result.get('severity', 0)
    icon = DECISION_ICONS.get(dec, '?')
    bar  = '█' * int(sev * 20) + '░' * (20 - int(sev * 20))

    if scenario_name:
        print(f'\n{BOLD}Scenario: {scenario_name}{RESET}')

    print(color(f'{icon} Decision : {dec}', dec))
    print(f'   Risk bar : [{bar}] {sev*100:.0f}%')
    print(f'   EN       : {result.get("alert_en", "")}')
    print(f'   BN       : {result.get("alert_bn", "")}')
    print(f'   Reason   : {result.get("reason", "")}')

    if show_scores:
        s = result.get('scores', {})
        m = result.get('meta',   {})
        print(f'   Scores   : RF={s.get("rf",0):.3f} XGB={s.get("xgb",0):.3f} '
              f'IF={s.get("if",0):.3f} AE={s.get("ae",0):.3f} '
              f'ZD={s.get("zd",0):.3f} TRAV={s.get("trav",0):.3f} '
              f'Fused={s.get("fused",0):.3f}')
        print(f'   Meta     : conflict={m.get("conflict",0):.3f} '
              f'zero_day={m.get("is_zero_day",False)} '
              f'trav_trusted={m.get("trav_trusted",False)} '
              f'latency={m.get("latency_ms",0)}ms')


# ══════════════════════════════════════════════════════════════════════════
# SHOWCASE SCENARIOS (Block 13 equivalent)
# ══════════════════════════════════════════════════════════════════════════

def run_showcase(client: SafeNestClient, loader: DatasetLoader):
    """
    Fires the 5 exact showcase scenarios from Block 13 against the live API.
    Each scenario uses a real dataset row as the flow features,
    but overrides session context (hour, bw_kbps, country etc.) to simulate
    the exact scenario being demonstrated.
    """
    separator('═')
    print(f'{BOLD}SAFENEST GUARD — 5 SHOWCASE SCENARIOS{RESET}')
    print('Firing real dataset rows with controlled session context.')
    separator('═')

    # Reset dashboard + device profiles for a clean run
    client.reset_dashboard()
    client.reset_devices()
    print('Dashboard and device profiles reset for clean demo run.')

    # Step 1: Pre-register devices so they are REGISTERED (not UNREGISTERED)
    # This prevents NewDeviceHandler from blocking ML model decisions
    known_devices = ['home_camera', 'home_lock', 'home_router',
                     'nsu_cam_floor3', 'nsu_smart_lock', 'nsu_rfid_301',
                     'nsu_cam_entrance', 'home_cam_front', 'home_door_lock']
    print('\nPre-registering known devices ...')
    result = client.register_device(known_devices)
    print(f'  Registered: {result.get("registered", [])}')

    # Step 2: Register TRAV profiles (same as notebook Block 8)
    print('\nRegistering TRAV profiles for showcase devices ...')
    registrations = [
        ('home_camera', 9,  2000, 250, 'BD'),
        ('home_camera', 17, 1950, 200, 'BD'),
        ('home_camera', 22, 1800, 180, 'AU'),
        ('home_camera', 21, 1750, 160, 'AU'),
        ('home_lock',   7,  40,   5,   'BD'),
        ('home_lock',   23, 35,   3,   'BD'),
        ('home_router', 9,  500,  30,  'BD'),
        ('home_router', 14, 480,  25,  'BD'),
    ]
    for dev, h, bw, dur, ctry in registrations:
        client.register_session(dev, h, bw, dur, ctry)
    print(f'  Registered {len(registrations)} sessions across 3 devices.\n')

    # ── The 5 scenarios ──────────────────────────────────────────────────
    scenarios = [
        {
            'name'       : '1. Normal home camera — BD 9am',
            'description': 'Owner at home watching camera normally. Expect: ✅ SAFE',
            'flow_type'  : 'benign',
            'attack_type': None,
            'device_id'  : 'home_camera',
            'hour'       : 9,
            'bw_kbps'    : 2000,
            'dur_sec'    : 250,
            'country'    : 'BD',
            'device_type': 'camera',
            'dst_port'   : 443,
            'expect'     : 'SAFE',
        },
        {
            'name'       : '2. Owner from Australia — 10pm',
            'description': 'Legitimate owner watching from abroad. Expect: ✅ SAFE (TRAV recognizes)',
            'flow_type'  : 'benign',
            'attack_type': None,
            'device_id'  : 'home_camera',
            'hour'       : 22,
            'bw_kbps'    : 1800,
            'dur_sec'    : 200,
            'country'    : 'AU',
            'device_type': 'camera',
            'dst_port'   : 443,
            'expect'     : 'SAFE',
        },
        {
            'name'       : '3. Hacker from Australia — 3am',
            'description': 'Same country as owner but 3am, 90Mbps, 10sec. Expect: 🚨 ALERT',
            'flow_type'  : 'attack',
            'attack_type': None,   # any attack type
            'device_id'  : 'home_camera',
            'hour'       : 3,
            'bw_kbps'    : 90000,
            'dur_sec'    : 10,
            'country'    : 'AU',
            'device_type': 'camera',
            'dst_port'   : 80,
            'expect'     : 'ALERT',
        },
        {
            'name'       : '4. New IoT device joins network',
            'description': 'Brand new device — no profile. Expect: ⚠️  CAUTION (UNREGISTERED)',
            'flow_type'  : 'benign',
            'attack_type': None,
            'device_id'  : 'new_smart_tv_living_room',
            'hour'       : 12,
            'bw_kbps'    : 500,
            'dur_sec'    : 60,
            'country'    : 'BD',
            'device_type': 'tv',
            'dst_port'   : 80,
            'expect'     : 'CAUTION',
        },
        {
            'name'       : '5. DDoS / zero-day attack',
            'description': 'Massive DDoS from China at 3am. Expect: 🚨 ALERT',
            'flow_type'  : 'attack',
            'attack_type': None,
            'device_id'  : 'home_camera',
            'hour'       : 3,
            'bw_kbps'    : 95000,
            'dur_sec'    : 5,
            'country'    : 'CN',
            'device_type': 'camera',
            'dst_port'   : 80,
            'expect'     : 'ALERT',
        },
    ]

    passed = 0
    for sc in scenarios:
        separator()
        print(f'{BOLD}{sc["name"]}{RESET}')
        print(f'  {sc["description"]}')

        # Get real dataset row
        flow = loader.sample_row(
            label       = sc['flow_type'],
            attack_type = sc['attack_type'] or loader.random_attack_type()
        )

        try:
            result = client.predict(
                flow        = flow,
                device_id   = sc['device_id'],
                hour        = sc['hour'],
                bw_kbps     = sc['bw_kbps'],
                dur_sec     = sc['dur_sec'],
                country     = sc['country'],
                device_type = sc['device_type'],
                dst_port    = sc['dst_port'],
            )

            print_result(result, show_scores=True)

            # Post to dashboard (shows in browser)
            client.post_showcase(result, label=sc['name'])

            got      = result['decision']
            expected = sc['expect']
            if got == expected:
                print(f'  {GREEN}✓ PASS — got {got} as expected{RESET}')
                passed += 1
            else:
                print(f'  {YELLOW}△ NOTE — expected {expected}, got {got}{RESET}')
                print(f'    (TRAV/model scores affect outcome — see scores above)')

        except Exception as e:
            print(f'  {RED}✗ ERROR: {e}{RESET}')

    separator('═')
    print(f'{BOLD}Showcase result: {passed}/{len(scenarios)} matched expected decisions{RESET}')
    print('Note: TRAV-dependent scenarios (2, 3) depend on registered profile history.')
    separator('═')


# ══════════════════════════════════════════════════════════════════════════
# RANDOM SAMPLING
# ══════════════════════════════════════════════════════════════════════════

def run_random(client: SafeNestClient, loader: DatasetLoader, n: int = 10):
    """
    Sample N random rows from the dataset (mix of benign and attacks)
    and fire them at the API. Shows distribution of decisions.
    """
    separator('═')
    print(f'{BOLD}RANDOM SAMPLING — {n} flows{RESET}')
    separator('═')

    devices = ['home_camera', 'home_lock', 'home_router']
    # Make sure these devices are registered before random testing
    client.register_device(devices)
    countries = ['BD', 'BD', 'BD', 'AU', 'CN', 'RU']
    device_types = {'home_camera':'camera','home_lock':'lock','home_router':'router'}

    counts = {'SAFE':0,'CAUTION':0,'ALERT':0,'REVIEW':0}
    latencies = []

    for i in range(n):
        # Alternate benign / attack
        is_attack   = (i % 3 != 0)   # 2/3 attacks, 1/3 benign
        device_id   = np.random.choice(devices)
        country     = np.random.choice(countries)
        hour        = int(np.random.randint(0, 24))
        bw_kbps     = float(np.random.choice([200, 1800, 2000, 50000, 90000]))
        dur_sec     = float(np.random.choice([5, 60, 200, 300, 3600]))
        flow        = loader.sample_row('attack' if is_attack else 'benign')

        try:
            result = client.predict(
                flow        = flow,
                device_id   = device_id,
                hour        = hour,
                bw_kbps     = bw_kbps,
                dur_sec     = dur_sec,
                country     = country,
                device_type = device_types.get(device_id,'unknown'),
                dst_port    = int(np.random.choice([80, 443, 23, 9090])),
            )
            dec = result['decision']
            sev = result['severity']
            lat = result['meta']['latency_ms']
            counts[dec] = counts.get(dec, 0) + 1
            latencies.append(lat)

            # Post to dashboard
            client.post_random(result,
                src     = 'ATTACK' if is_attack else 'BENIGN',
                bw      = bw_kbps,
                country = country)

            icon = DECISION_ICONS.get(dec,'?')
            flow_type = 'ATTACK' if is_attack else 'BENIGN'
            print(color(
                f'  [{i+1:2d}] {icon} {dec:<8} '
                f'sev={sev:.2f}  src={flow_type:<7}  '
                f'device={device_id:<16}  country={country}  '
                f'bw={bw_kbps:>7.0f}kbps  {lat:.0f}ms',
                dec
            ))
        except Exception as e:
            print(f'  [{i+1:2d}] {RED}ERROR: {e}{RESET}')

    separator()
    print(f'\n{BOLD}Summary ({n} flows){RESET}')
    for dec, cnt in sorted(counts.items(), key=lambda x:-x[1]):
        bar = '█' * cnt + '░' * (n - cnt)
        print(color(f'  {dec:<8} {cnt:3d}  [{bar[:40]}]', dec))
    if latencies:
        print(f'\n  Latency: avg={np.mean(latencies):.1f}ms  '
              f'min={min(latencies):.1f}ms  max={max(latencies):.1f}ms')
    separator('═')


# ══════════════════════════════════════════════════════════════════════════
# BATCH TEST
# ══════════════════════════════════════════════════════════════════════════

def run_batch_test(client: SafeNestClient, loader: DatasetLoader):
    """Send all 5 showcase scenarios as a single batch request."""
    separator('═')
    print(f'{BOLD}BATCH TEST — All 5 scenarios in one request{RESET}')
    separator('═')

    batch_requests = [
        {'flow': loader.sample_row('benign'), 'device_id':'home_camera',
         'hour':9,  'bw_kbps':2000,  'dur_sec':250, 'country':'BD', 'device_type':'camera'},
        {'flow': loader.sample_row('benign'), 'device_id':'home_camera',
         'hour':22, 'bw_kbps':1800,  'dur_sec':200, 'country':'AU', 'device_type':'camera'},
        {'flow': loader.sample_row('attack'), 'device_id':'home_camera',
         'hour':3,  'bw_kbps':90000, 'dur_sec':10,  'country':'AU', 'device_type':'camera'},
        {'flow': loader.sample_row('benign'), 'device_id':'new_smart_tv',
         'hour':12, 'bw_kbps':500,   'dur_sec':60,  'country':'BD', 'device_type':'tv'},
        {'flow': loader.sample_row('attack'), 'device_id':'home_camera',
         'hour':3,  'bw_kbps':95000, 'dur_sec':5,   'country':'CN', 'device_type':'camera'},
    ]

    labels = ['Normal BD 9am','Owner AU 10pm','Hacker AU 3am','New device','DDoS CN 3am']

    t0 = time.time()
    response = client.predict_batch(batch_requests)
    total_ms = (time.time() - t0) * 1000

    results = response.get('results', [])
    for i, (label, result) in enumerate(zip(labels, results)):
        dec  = result.get('decision','ERR')
        sev  = result.get('severity', 0)
        icon = DECISION_ICONS.get(dec,'?')
        print(color(f'  [{i+1}] {icon} {dec:<8} sev={sev:.2f}  {label}', dec))

    print(f'\n  Batch of {len(results)} flows completed in {total_ms:.0f}ms total')
    separator('═')


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='SafeNest Guard API test client')
    parser.add_argument('--url',          default=DEFAULT_API_URL,
                        help='API base URL (default: http://localhost:5000)')
    parser.add_argument('--dataset',      default=None,
                        help='Path to CICIoT2023.csv (auto-detected if not set)')
    parser.add_argument('--showcase-only', action='store_true',
                        help='Run only the 5 showcase scenarios')
    parser.add_argument('--random',       type=int, default=15,
                        help='Number of random flows to test (default: 15)')
    parser.add_argument('--batch',        action='store_true',
                        help='Also run a batch test of all 5 scenarios')
    args = parser.parse_args()

    # ── Step 1: Health check ──────────────────────────────────────────────
    print(f'\n{BOLD}SafeNest Guard Test Client{RESET}')
    separator('═')
    print(f'API: {args.url}')
    print('Checking server health ...')

    client = SafeNestClient(args.url)
    try:
        health = client.health()
        print(f'  Status  : {GREEN}{health["status"]}{RESET}')
        print(f'  Features: {health["feature_count"]}')
        print(f'  AE      : {health["autoencoder"]}')
        print(f'  Devices : {health["trav_devices"]}')
    except requests.exceptions.ConnectionError:
        print(f'{RED}Cannot connect to {args.url}{RESET}')
        print('Start the API first:  python safenest_api.py')
        sys.exit(1)

    # ── Step 2: Get feature names ─────────────────────────────────────────
    print('\nFetching feature names from API ...')
    feature_names = client.get_features()
    print(f'  {len(feature_names)} features: {feature_names[:5]} ... {feature_names[-3:]}')

    # ── Step 3: Load dataset ──────────────────────────────────────────────
    dataset_path = args.dataset
    if dataset_path is None:
        # Auto-detect — balanced dataset first, full dataset as fallback
        candidates = [
            './dataset/safenest_test_balanced.csv',        # small balanced file (recommended)
            './dataset/CICIoT2023.csv',                    # full dataset fallback
        ]
        for c in candidates:
            if os.path.exists(c):
                dataset_path = c
                break

    if dataset_path is None or not os.path.exists(dataset_path):
        print(f'\n{YELLOW}CICIoT2023.csv not found. Using random zero-filled flows.{RESET}')
        print('Pass --dataset /path/to/CICIoT2023.csv for real data.\n')

        class FakeLoader:
            def __init__(self, feature_names):
                self.feature_names = feature_names
                self.attack_rows   = {'DDoS': 'fake', 'PortScan': 'fake'}
            def sample_row(self, label='benign', attack_type=None):
                rng = np.random.RandomState(int(time.time() * 1000) % 2**31)
                if label == 'attack':
                    # Simulate attack-like feature values
                    vec = rng.exponential(scale=2.0, size=len(self.feature_names))
                else:
                    vec = rng.uniform(0, 0.5, size=len(self.feature_names))
                return {f: float(v) for f, v in zip(self.feature_names, vec)}
            def random_attack_type(self):
                return 'DDoS'

        loader = FakeLoader(feature_names)
    else:
        print(f'\nDataset: {dataset_path}')
        loader = DatasetLoader(dataset_path, feature_names)
        loader.load(nrows=50_000)

    separator()

    # ── Step 4: Run tests ─────────────────────────────────────────────────
    run_showcase(client, loader)

    if not args.showcase_only:
        print()
        run_random(client, loader, n=args.random)

    if args.batch:
        print()
        run_batch_test(client, loader)

    print(f'\n{BOLD}All tests complete.{RESET}')
    print(f'{GREEN}Dashboard: {args.url}  (open in browser){RESET}')
    print(f'All results are visible in the dashboard in real-time.')


if __name__ == '__main__':
    main()
