# STEM Diagram Generator - Web UI

A Next.js web interface for generating physics diagrams from problem descriptions.

## Architecture

```
┌─────────────────┐      HTTP      ┌─────────────────┐      Python      ┌──────────────────────┐
│                 │  ──────────>    │                 │  ─────────────>  │                      │
│   Next.js UI    │                 │   Flask API     │                  │  UnifiedDiagram      │
│   (Port 3000)   │  <──────────    │   (Port 5000)   │  <─────────────  │  Pipeline            │
│                 │      JSON       │                 │      DiagramResult│                      │
└─────────────────┘                 └─────────────────┘                  └──────────────────────┘
```

## Setup

### 1. Install Python Dependencies

```bash
# Install Flask API requirements
pip install -r requirements-api.txt

# Existing pipeline requirements (if not already installed)
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies

```bash
cd diagram-ui
npm install
```

### 3. Start the Backend (Flask API)

```bash
# From project root
python3 api_server.py
```

This starts the Flask API server on `http://localhost:5000`

### 4. Start the Frontend (Next.js)

```bash
# In another terminal
cd diagram-ui
npm run dev
```

This starts the Next.js development server on `http://localhost:3000`

## Usage

1. Open your browser to `http://localhost:3000`
2. Enter a physics problem description in the text area
3. Click "Generate Diagram"
4. View the generated SVG diagram and analysis metadata

## Example Problems

### Capacitor with Dielectric

```
A parallel-plate capacitor has plates of area 0.12 m² and a separation of 1.2 cm.
A battery charges the plates to a potential difference of 120 V and is then disconnected.
A dielectric slab of thickness 4.0 mm and dielectric constant κ = 4.8 is then placed symmetrically
between the plates. What is the magnitude of the electric field in the dielectric after insertion?
```

### Series Capacitors

```
A potential difference of 300 V is applied to a series connection of two capacitors
of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF. The charged capacitors are then disconnected
from the battery and from each other. They are then reconnected with plates of the same signs
wired together (positive to positive, negative to negative). What is the charge on capacitor C₁?
```

### Cylindrical Capacitor

```
As a safety engineer, you must evaluate the practice of storing flammable conducting liquids
in nonconducting containers. The company has been using a squat, cylindrical plastic container of
radius r = 0.20 m and filling it to height h = 10 cm. The exterior surface of the container commonly
acquires a negative charge density of magnitude 2.0 μC/m² (approximately uniform).
```

## API Endpoints

### POST /api/generate

Generate a diagram from problem text.

**Request:**
```json
{
  "problem_text": "A parallel-plate capacitor has plates of area 0.12 m²..."
}
```

**Response:**
```json
{
  "svg": "<svg>...</svg>",
  "metadata": {
    "complexity_score": 0.35,
    "selected_strategy": "symbolic_physics",
    "property_graph_nodes": 12,
    "property_graph_edges": 8,
    "ontology_validation": {...},
    "nlp_tools_used": ["openie"]
  }
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "pipeline": "unified_diagram_pipeline.py",
  "features": {
    "property_graph": true,
    "nlp_enrichment": true,
    "complexity_assessment": true,
    "strategic_planning": true,
    "ontology_validation": true
  }
}
```

## Features

### Frontend (Next.js + React)
- Text input for problem descriptions
- Real-time diagram generation
- Loading states and error handling
- Responsive design with Tailwind CSS
- Metadata display (complexity, strategy, graph stats)

### Backend (Flask)
- RESTful API wrapping UnifiedDiagramPipeline
- CORS support for cross-origin requests
- Error handling and logging
- Production-ready configuration

### Pipeline (Python)
- NLP enrichment (OpenIE triple extraction)
- Property graph construction
- Complexity assessment
- Strategic planning
- Ontology validation
- Domain-specific scene interpreters

## Development

### Frontend Development

```bash
cd diagram-ui
npm run dev    # Start dev server
npm run build  # Build for production
npm start      # Start production server
```

### Backend Development

```bash
python3 api_server.py  # Runs in debug mode by default
```

### Environment Variables

Create `diagram-ui/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
```

For production, update to your API server URL.

## Troubleshooting

### Port Already in Use

If port 5000 or 3000 is already in use:

```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### CORS Errors

Make sure Flask-CORS is installed:

```bash
pip install flask-cors
```

### Module Not Found

Ensure you're running from the project root:

```bash
cd /Users/Pramod/projects/STEM-AI/pipeline_universal_STEM
python3 api_server.py
```

## Production Deployment

### Backend (Flask)

Use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### Frontend (Next.js)

Build and export:

```bash
cd diagram-ui
npm run build
npm start
```

Or deploy to Vercel:

```bash
vercel deploy
```

## Architecture Details

### Data Flow

1. User enters problem text in Next.js UI
2. Frontend sends POST to `/api/generate` (Next.js API route)
3. Next.js proxies request to Flask backend
4. Flask calls `UnifiedDiagramPipeline.generate(problem_text)`
5. Pipeline executes 7 phases:
   - Phase 1: NLP Enrichment (OpenIE)
   - Phase 2: Property Graph Construction
   - Phase 3: Complexity Assessment
   - Phase 4: Scene Synthesis (CapacitorInterpreter)
   - Phase 5: Ontology Validation
   - Phase 6: Layout Optimization
   - Phase 7: SVG Rendering
6. Flask returns SVG + metadata as JSON
7. Next.js displays diagram and metadata to user

### Component Structure

```
diagram-ui/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Home page
│   ├── globals.css         # Tailwind styles
│   └── api/
│       └── generate/
│           └── route.ts    # API route handler
├── components/
│   └── DiagramGenerator.tsx # Main UI component
├── package.json
├── tsconfig.json
├── next.config.js
└── tailwind.config.js
```

## License

Same as parent project.

## Contributors

Generated with Claude Code on November 10, 2025.
