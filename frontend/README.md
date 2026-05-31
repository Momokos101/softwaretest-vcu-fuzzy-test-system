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
│   ├── AutoTestDesignV2.tsx     FR 7.0 workflow: Concept / Coverage / Strategy / Test Cases / Prompts / Results / Optimize
│   ├── RequirementInput.tsx    FR 1.0/1.1 — import and parse requirements
│   ├── RiskAnalysis.tsx        FR 2.0 — risk scoring and prioritization
│   ├── TestCaseDesign.tsx      FR 3.0 — EP/BVA/Decision Table generation
│   ├── ExportCenter.tsx        FR 6.0 — JSON/CSV/Excel export
│   ├── Sidebar.tsx             Navigation sidebar
│   ├── TopNav.tsx              Top navigation bar
│   └── ui/                     shadcn/ui base components
├── services/
│   └── api.ts                  Axios client + all API methods
└── ...
```

## Navigation Pages

| View Key | Component | Description |
|----------|-----------|-------------|
| `autotest-v2` | AutoTestDesignV2 | FR 7.0 workflow hub |
| `requirements` | RequirementInput | Import and parse requirements |
| `risk-analysis` | RiskAnalysis | Risk scoring |
| `test-design` | TestCaseDesign | Generate test cases |
| `export` | ExportCenter | Export test artifacts |
