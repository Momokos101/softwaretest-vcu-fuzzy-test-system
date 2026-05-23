# AutoTestDesign — AI-Driven Test Design Tool

An AI-powered automated test design tool that performs requirements analysis, risk assessment, and systematic test case generation, aligned with ISO/IEC/IEEE standards and ISTQB Foundation Level principles.

**Target Application**: VCU (Vehicle Control Unit) Wake-Sleep Control Module

---

## Project Overview

AutoTestDesign is the tool. The VCU Wake-Sleep Control Module is the self-chosen target application used to demonstrate the tool's effectiveness.

The tool implements:

| FR | Feature | Status |
|----|---------|--------|
| FR 1.0 | Input / Parsing — ingest requirements from CSV, plain text, or direct form input | Implemented |
| FR 1.1 | Requirement Structuring — parse Input Fields, Data Ranges, Conditions, Expected Actions | Implemented |
| FR 2.0 | Risk Analysis & Prioritization — assign Risk Score and Priority (High/Medium/Low) | Implemented |
| FR 3.0 | Black-Box Test Design — Equivalence Partitioning, Boundary Value Analysis, Decision Tables | Implemented |
| FR 4.0 | White-Box Test Modeling — State Transition Diagram and test sequence generation | Future extension |
| FR 5.0 | Test Oracle Generation — synthesize Expected Result from requirement + test data | Partially implemented |
| FR 6.0 | Output & Export — JSON, CSV, Excel with traceability matrix | Implemented |
| FR 7.0 | Test Suite Optimization — risk-based prioritization and coverage minimization | Future extension |

---

## System Architecture

```
AutoTestDesign/
├── backend/          Python + FastAPI — all FR logic and API endpoints
├── frontend/         React + TypeScript + Tailwind CSS — interactive UI
├── vcu_simulator/    Python + FastAPI — target VCU behavior simulator
├── tests/            pytest test scripts for the VCU target application
└── docs/             Design plan and project documents
```

**Runtime Services**

The demo uses three local services:

| Service | Directory | Command | URL |
|---------|-----------|---------|-----|
| VCU Simulator | `vcu_simulator/` | `conda run -n ST uvicorn main:app --host 127.0.0.1 --port 8001` | http://localhost:8001 |
| AutoTestDesign Backend | `backend/` | `conda run -n ST python run_server.py` | http://localhost:8000 |
| AutoTestDesign Frontend | `frontend/` | `npm run dev` | http://localhost:3000 |

The backend calls the simulator over HTTP. `VCU_SIMULATOR_URL` can override the default simulator URL (`http://localhost:8001`).

**FR API Endpoints**

| FR | Capability | API |
|----|------------|-----|
| FR 1.0 | CSV / text / form requirement import | `POST /api/requirements/import/csv`, `POST /api/requirements/import/text`, `POST /api/requirements/import/form` |
| FR 1.1 | Requirement structuring and review | `GET /api/requirements`, `PUT /api/requirements/{id}`, `POST /api/requirements/{id}/parse`, `PUT /api/requirements/{id}/parsed` |
| FR 2.0 | Risk analysis and manual score adjustment | `POST /api/risk-analysis/{id}`, `GET /api/risk-analysis/matrix/data`, `PUT /api/risk-analysis/{id}` |
| FR 3.0 | EP / BVA / Decision Table generation | `POST /api/test-cases/generate`, `GET /api/test-cases`, `PUT /api/test-cases/{id}` |
| FR 3.0 / FR 5.0 | Test execution and oracle comparison | `POST /api/test-cases/{id}/execute`, `POST /api/test-cases/execute/batch` |
| FR 6.0 | JSON / CSV / Excel export | `POST /api/export` |

**Feature Coverage**

- FR 1.0 / 1.1 imports requirements from CSV, free text, and direct form input, then extracts input fields, data ranges, conditions, and actions through deterministic regex rules.
- FR 2.0 uses the specified weighted risk formula on a 0-10 scale: Criticality 35%, Boundary Sensitivity 25%, Complexity 20%, State Impact 15%, Testability 5%.
- FR 3.0 generates EP, BVA, and Decision Table cases for the five VCU simulator signals. CC2 BVA uses the required seven points: `4.7 / 4.8 / 4.9 / 6.3 / 7.7 / 7.8 / 7.9`.
- Test execution calls the VCU simulator `/simulate`, `/simulate/sleep`, and `/simulate/batch` endpoints and compares `result_type`, `test_status`, and V2 `vehicle_state` (`9/10/11`) against the generated oracle.
- Interactive Review is implemented at every stage: requirement text editing, parsed structure editing, risk score adjustment, and test case editing.
- FR 6.0 exports requirements, risk results, test cases, execution results, and the traceability matrix to JSON, CSV, or Excel.

**Demo and Submission Materials**

| Material | Path |
|---|---|
| Demo VCU requirements CSV | `docs/demo_vcu_requirements.csv` |
| Member 2 tool developer deliverables | `docs/Member2_Tool_Developer_Deliverables.md` |
| Prompt and rule design notes | `docs/prompts.md` |
| VCU simulator API handover | `docs/tasks/simulator_api_for_tool.md` |

**Tech Stack**

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, FastAPI, SQLite |
| Frontend | React 18, TypeScript, Tailwind CSS, Vite |
| AI Component | PyTorch GAN model (Conv1D conditional GAN) |
| Test Execution | pytest, pytest-parametrize |
| Export | pandas, openpyxl |

---

## Quick Start (New Server Deployment)

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd softwaretest-vcu-fuzzy-test-system
```

### 2. Backend Setup

```bash
cd backend
conda run -n ST python run_server.py
```

Backend runs at: http://localhost:8000  
API docs: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:3000

### 4. VCU Simulator Setup

```bash
cd vcu_simulator
conda run -n ST uvicorn main:app --host 127.0.0.1 --port 8001
```

Simulator API docs: http://localhost:8001/docs

### 5. One-Command Setup (macOS / Linux)

```bash
chmod +x setup.sh
./setup.sh
```

---

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
```

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Project Structure

```
softwaretest-vcu-fuzzy-test-system/
├── backend/
│   ├── api/
│   │   ├── main.py                   FastAPI app entry point
│   │   ├── routers/                  API route handlers
│   │   │   ├── requirements.py       FR 1.0 / 1.1
│   │   │   ├── risk_analysis.py      FR 2.0
│   │   │   ├── test_design.py        FR 3.0
│   │   │   ├── export.py             FR 6.0
│   │   │   ├── test_plans.py         Test plan management
│   │   │   ├── test_tasks.py         Test task execution
│   │   │   ├── reports.py            Report generation
│   │   │   ├── constraints.py        Constraint management
│   │   │   ├── monitoring.py         Real-time monitoring
│   │   │   └── gan.py                GAN model inference
│   │   ├── services/                 Business logic
│   │   ├── models/                   Pydantic schemas
│   │   └── database/                 SQLite access layer
│   ├── configs/                      VCU model configuration
│   ├── nn/                           GAN neural network (Conv1D)
│   ├── data/                         VCU test data (.npy files)
│   ├── requirements.txt
│   └── run_server.py
├── frontend/
│   ├── src/
│   │   ├── components/               UI components
│   │   ├── pages/                    Page-level components
│   │   ├── services/api.ts           Axios API client
│   │   └── App.tsx                   Root component + routing
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   ├── test_e2e.py                   End-to-end tests
│   ├── test_api_routes.py            API route tests
│   └── test_baic_integration.py      VCU integration tests
├── docs/
│   └── DESIGN_PLAN.md               Full implementation design plan
├── setup.sh                         One-command setup script
├── .gitignore
└── README.md
```

---

## Key Design Decisions

- **Target application** is the VCU wake-sleep module — this is what the AutoTestDesign tool is applied to, not the tool itself.
- All FR modules share a common **requirement ID** as the linking key, enabling end-to-end traceability from requirement → risk score → test cases → export.
- Every stage supports **interactive review**: users can modify parsed structures, override risk scores, edit or delete generated test cases, and choose export scope.
- The GAN model generates additional "intelligent" test cases on top of the rule-based EP/BVA/Decision Table cases, giving the tool its "AI-driven" character.

---

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/

# Run only VCU integration tests
pytest tests/test_baic_integration.py -v

# Run with coverage report
pytest tests/ --cov=backend/api --cov-report=html
```

---

## License

Course project — for educational and research purposes only.
