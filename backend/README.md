# AutoTestDesign — Backend

FastAPI backend providing all AutoTestDesign tool logic and REST API endpoints.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
python run_server.py
```

- API base: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | Bind address |
| `API_PORT` | `8000` | Port number |
| `API_RELOAD` | `true` | Hot-reload (set `false` in production) |
| `VCU_SIMULATOR_URL` | `http://localhost:8001` | V2 VCU simulator base URL |
| `LLM_PROVIDER` | `openai_compatible` | `openai_compatible` or `anthropic` |
| `LLM_BASE_URL` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | LLM API base URL; use this to switch model gateways |
| `LLM_API_KEY` / `DASHSCOPE_API_KEY` | required | LLM API key; `LLM_API_KEY` takes precedence |
| `LLM_MODEL` | `qwen3.7-max` | Model name sent to the provider |
| `LLM_TIMEOUT_SECONDS` | `60` | LLM request timeout |
| `LLM_MAX_TOKENS` | `4096` | LLM response token budget |
| `LLM_TEMPERATURE` | `0.1` | LLM sampling temperature |
| `LLM_STREAM` | `true` | Use streaming chat completions for OpenAI-compatible providers |
| `LLM_ENABLE_THINKING` | `true` for DashScope URLs | Sends `extra_body={"enable_thinking": true}` |
| `LLM_RESPONSE_FORMAT` | `json_object` | Set `none` for gateways that reject OpenAI JSON mode |

## API Routes

| Prefix | File | Purpose |
|--------|------|---------|
| `/api/requirements` | `routers/requirements.py` | FR 1.0/1.1 — requirement import and parsing |
| `/api/risk-analysis` | `routers/risk_analysis.py` | FR 2.0 — risk scoring and prioritization |
| `/api/test-cases` | `routers/test_design.py` | FR 3.0 — EP, BVA, Decision Table generation |
| `/api/test-cases/{case_id}/execute` | `routers/test_design.py` | Single-case simulator execution |
| `/api/test-cases/execute/batch` | `routers/test_design.py` | Batch simulator execution |
| `/api/coverage-items` | `routers/autotest_review.py` | Interactive Review step 2 coverage management |
| `/api/strategies` | `routers/autotest_review.py` | Interactive Review step 3 strategy management |
| `/api/prompts` | `routers/autotest_review.py` | Interactive Review prompt editing |
| `/api/execute` | `routers/autotest_review.py` | V2 simulator execution |
| `/api/results/summary` | `routers/autotest_review.py` | Result summary statistics |
| `/api/improve` | `routers/autotest_review.py` | Second-round LLM test-augmentation suggestions |
| `/api/optimize/prioritize`, `/api/optimize/minimize` | `routers/autotest_review.py` | FR 7.0 — risk prioritization + coverage minimization |
| `/api/performance` | `routers/autotest_review.py` | Tool NFR timing metrics |
| `/api/export` | `routers/export.py` | FR 6.0 — JSON, CSV, Excel export |
| `/api/health` | `main.py` | Health check |

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
├── reports/              Generated report files
├── test_plans/           Saved test plan JSON files
├── v2_state/             Current editable V2 state mirrored by the UI
│   ├── requirements.json
│   ├── parsed_requirements.json
│   ├── risk_results.json
│   ├── coverage_items.json
│   ├── strategies.json
│   ├── prompts.json
│   ├── performance.json
│   └── test_cases.json
└── vcu/                  VCU test data and generated sequence artifacts
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
