# AutoTestDesign — Backend

FastAPI backend providing all AutoTestDesign tool logic and REST API endpoints.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 run_server.py
```

- API base: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | Bind address |
| `API_PORT` | `8000` | Port number |
| `API_RELOAD` | `true` | Hot-reload (set `false` in production) |

## API Routes

| Prefix | File | Purpose |
|--------|------|---------|
| `/api/requirements` | `routers/requirements.py` | FR 1.0/1.1 — requirement import and parsing |
| `/api/risk-analysis` | `routers/risk_analysis.py` | FR 2.0 — risk scoring and prioritization |
| `/api/test-design` | `routers/test_design.py` | FR 3.0 — EP, BVA, Decision Table generation |
| `/api/export` | `routers/export.py` | FR 6.0 — JSON, CSV, Excel export |
| `/api/test-plans` | `routers/test_plans.py` | Test plan CRUD |
| `/api/test-tasks` | `routers/test_tasks.py` | Test task execution |
| `/api/reports` | `routers/reports.py` | Report generation |
| `/api/constraints` | `routers/constraints.py` | Constraint management |
| `/api/monitoring` | `routers/monitoring.py` | Real-time metrics |
| `/api/gan` | `routers/gan.py` | GAN model inference |
| `/ws/test-tasks/{id}` | `main.py` | WebSocket real-time push |

## Key Files

| File | Purpose |
|------|---------|
| `run_server.py` | Server entry point |
| `setup_model.py` | Download / verify GAN model weights |
| `find_model.py` | Locate model weights on disk |
| `download_models.py` | Fetch model weights from remote |
| `example_usage.py` | Code examples for key services |

## Data Directory

```
data/
├── vcu/                  VCU test data (NumPy arrays)
│   ├── train_voltages.npy
│   ├── train_labels.npy
│   ├── test_voltages.npy
│   ├── test_labels.npy
│   └── metadata.json
├── test_plans/           Saved test plan JSON files
├── reports/              Generated report files
├── requirements/         Imported requirement JSON files  (created at runtime)
├── risk_analysis/        Risk analysis result files       (created at runtime)
└── test_cases/           Generated test case files        (created at runtime)
```

## VCU Model Configuration

Configuration files are in `configs/`:

| File | Description |
|------|-------------|
| `config_vcu_base.py` | Shared constants (voltage ranges, model path) |
| `config_vcu_data.py` | Database paths, anomaly thresholds |
| `config_vcu_model.py` | GAN architecture parameters |
| `config_vcu_train.py` | Training hyperparameters |

Key VCU constants used as test boundaries:

| Constant | Value | Meaning |
|----------|-------|---------|
| `CC2_MIN_VOLTAGE` | 4.8 V | Wake-up lower bound |
| `CC2_MAX_VOLTAGE` | 7.8 V | Wake-up upper bound |
| `SLEEP_VOLTAGE` | 12.0 V | Sleep trigger voltage |
| `VEHICLE_STATUS_MIN` | 30 | READY flag clear threshold |
| `VEHICLE_STATUS_MAX` | 170 | READY flag set threshold |
