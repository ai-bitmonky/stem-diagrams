# STEM Diagram Generator - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Flask (Backend)

```bash
pip3 install flask flask-cors
```

If blocked by proxy, try:
```bash
pip3 install --no-proxy=* flask flask-cors
```

### Step 2: Install Next.js Dependencies (Frontend)

```bash
cd diagram-ui
npm install
```

If blocked by proxy, try:
```bash
npm config delete proxy
npm config delete https-proxy
npm install
```

### Step 3: Start Both Servers

**Terminal 1** - Start Flask API:
```bash
python3 api_server.py
```

**Terminal 2** - Start Next.js UI:
```bash
cd diagram-ui
npm run dev
```

**Open browser:** http://localhost:3000

---

## 📁 Project Structure

```
pipeline_universal_STEM/
├── api_server.py                    # Flask API wrapping pipeline
├── unified_diagram_pipeline.py      # Main pipeline (production)
├── requirements-api.txt             # Flask dependencies
├── start_ui.sh                      # Automated startup script
│
├── diagram-ui/                      # Next.js frontend
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   │
│   ├── app/
│   │   ├── layout.tsx              # Root layout
│   │   ├── page.tsx                # Home page
│   │   ├── globals.css             # Tailwind styles
│   │   └── api/
│   │       └── generate/
│   │           └── route.ts        # API route handler
│   │
│   └── components/
│       └── DiagramGenerator.tsx    # Main UI component
│
├── core/                           # Pipeline components
│   ├── interpreters/
│   │   └── capacitor_interpreter.py
│   ├── nlp/
│   ├── knowledge_graph/
│   └── ...
│
└── output/                         # Generated diagrams
    └── batch_2_generated/
```

---

## 🎯 Usage

1. **Open browser:** http://localhost:3000

2. **Enter a problem description:**
   ```
   A parallel-plate capacitor has plates of area 0.12 m² and a
   separation of 1.2 cm. A battery charges the plates to a potential
   difference of 120 V.
   ```

3. **Click "Generate Diagram"**

4. **View results:**
   - SVG diagram display
   - Complexity score
   - Strategy used
   - Property graph statistics

---

## 📊 Example Problems

### Capacitor with Dielectric
```
A parallel-plate capacitor has plates of area 0.12 m² and a separation of 1.2 cm.
A battery charges the plates to a potential difference of 120 V and is then disconnected.
A dielectric slab of thickness 4.0 mm and dielectric constant κ = 4.8 is then placed
symmetrically between the plates.
```

### Series Capacitors
```
A potential difference of 300 V is applied to a series connection of two capacitors
of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF.
```

### Cylindrical Capacitor
```
A cylindrical plastic container of radius r = 0.20 m is filled to height h = 10 cm
with conducting liquid. The exterior surface acquires a charge density of 2.0 μC/m².
```

---

## 🔧 Troubleshooting

### Flask not installed?
```bash
pip3 install flask flask-cors
```

### npm install fails?
```bash
npm config delete proxy
npm config delete https-proxy
cd diagram-ui && npm install
```

### Port already in use?
```bash
# Kill port 5000 (Flask)
lsof -ti:5000 | xargs kill -9

# Kill port 3000 (Next.js)
lsof -ti:3000 | xargs kill -9
```

### CORS error in browser?
1. Make sure Flask-CORS is installed: `pip3 install flask-cors`
2. Restart Flask API: `python3 api_server.py`

---

## 🎨 Features

### Frontend
- ✅ Modern, responsive UI with Tailwind CSS
- ✅ Real-time diagram generation
- ✅ Loading states and error handling
- ✅ Metadata display (complexity, strategy, graph stats)

### Backend
- ✅ RESTful API with Flask
- ✅ CORS support for cross-origin requests
- ✅ Integration with UnifiedDiagramPipeline
- ✅ Comprehensive error handling

### Pipeline
- ✅ 7-phase generation process
- ✅ NLP enrichment (OpenIE)
- ✅ Property graph construction
- ✅ Complexity assessment
- ✅ Strategic planning
- ✅ Ontology validation
- ✅ Layout optimization
- ✅ SVG rendering

---

## 📚 Documentation

- [SETUP_UI.md](SETUP_UI.md) - Detailed setup instructions
- [README_UI.md](README_UI.md) - Comprehensive documentation
- [UI_IMPLEMENTATION_SUMMARY.md](UI_IMPLEMENTATION_SUMMARY.md) - Implementation details

---

## 🚀 Advanced Usage

### Automated Startup (Linux/Mac)
```bash
bash start_ui.sh
```

### Production Deployment

Backend:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

Frontend:
```bash
cd diagram-ui
npm run build
npm start
```

---

## 🔍 API Endpoints

### POST /api/generate
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"problem_text": "A parallel-plate capacitor..."}'
```

### GET /api/health
```bash
curl http://localhost:5000/api/health
```

---

## ✅ Checklist

Before first run:
- [ ] Flask installed (`pip3 install flask flask-cors`)
- [ ] Node.js dependencies installed (`cd diagram-ui && npm install`)
- [ ] Flask API running on port 5000
- [ ] Next.js UI running on port 3000
- [ ] Browser open to http://localhost:3000

---

**Questions?** See [SETUP_UI.md](SETUP_UI.md) for detailed troubleshooting.

**Generated:** November 10, 2025
