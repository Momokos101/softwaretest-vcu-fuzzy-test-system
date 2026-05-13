# AutoTestDesign — Frontend

React + TypeScript + Tailwind CSS frontend for the AutoTestDesign tool.

## Setup

```bash
npm install
npm run dev
```

Frontend runs at: http://localhost:3000  
All `/api` and `/ws` requests are proxied to http://localhost:8000

## Environment Variables

Create a `.env` file in this directory:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Build for Production

```bash
npm run build       # outputs to dist/
npm run preview     # preview the production build locally
```

## Tech Stack

| Technology | Role |
|-----------|------|
| React 18 | UI framework |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| Vite | Build tool |
| Axios | HTTP client |
| Lucide React | Icons |
| Sonner | Toast notifications |
| shadcn/ui | UI component library |

## Source Structure

```
src/
├── App.tsx                     Root component with view routing
├── components/
│   ├── Dashboard.tsx           Overview dashboard
│   ├── RequirementInput.tsx    FR 1.0/1.1 — import and parse requirements
│   ├── RiskAnalysis.tsx        FR 2.0 — risk scoring and prioritization
│   ├── TestCaseDesign.tsx      FR 3.0 — EP/BVA/Decision Table generation
│   ├── TestManagement.tsx      Test plan and task management
│   ├── TestMonitoring.tsx      Real-time test monitoring
│   ├── ResultAnalysis.tsx      Result analysis and charts
│   ├── ReportCenter.tsx        Report generation and download
│   ├── ExportCenter.tsx        FR 6.0 — JSON/CSV/Excel export
│   ├── SystemSettings.tsx      System configuration
│   ├── Sidebar.tsx             Navigation sidebar
│   ├── TopNav.tsx              Top navigation bar
│   └── ui/                     shadcn/ui base components
├── pages/                      Legacy JSX page components
├── services/
│   └── api.ts                  Axios client + all API methods
├── utils/
│   └── websocket.ts            WebSocket connection manager
└── contexts/
    └── RoleContext.tsx          User role context
```

## Navigation Pages

| View Key | Component | Description |
|----------|-----------|-------------|
| `dashboard` | Dashboard | System overview |
| `requirements` | RequirementInput | Import and parse requirements |
| `risk-analysis` | RiskAnalysis | Risk scoring |
| `test-design` | TestCaseDesign | Generate test cases |
| `tests` | TestManagement | Manage test plans and tasks |
| `monitoring` | TestMonitoring | Real-time task monitoring |
| `analysis` | ResultAnalysis | Result charts and anomaly list |
| `export` | ExportCenter | Export test artifacts |
| `reports` | ReportCenter | Generated reports |
| `settings` | SystemSettings | System settings |
