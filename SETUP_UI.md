# STEM Diagram Generator - UI Setup Instructions

## Quick Start

### 1. Install Python Dependencies

The Flask API requires `flask` and `flask-cors`. Install them with:

```bash
pip3 install flask flask-cors
```

**If behind a proxy:**
```bash
# Try with proxy
pip3 install --proxy=http://your-proxy:port flask flask-cors

# Or without proxy
pip3 install --no-proxy=* flask flask-cors

# Or download manually and install offline
```

### 2. Install Node.js Dependencies

```bash
cd diagram-ui
npm install
```

**If npm install fails due to proxy:**

Option A: Configure npm proxy
```bash
npm config set proxy http://your-proxy:port
npm config set https-proxy http://your-proxy:port
npm install
```

Option B: Disable proxy
```bash
npm config delete proxy
npm config delete https-proxy
npm install
```

Option C: Use yarn instead
```bash
yarn install
```

### 3. Start Both Servers

**Option A: Automated startup (Linux/Mac)**
```bash
./start_ui.sh
```

**Option B: Manual startup**

Terminal 1 (Flask API):
```bash
python3 api_server.py
```

Terminal 2 (Next.js UI):
```bash
cd diagram-ui
npm run dev
```

### 4. Open Browser

Navigate to: **http://localhost:3000**

## Usage

1. Enter a physics problem description in the text area
2. Click "Generate Diagram"
3. View the generated SVG diagram and metadata

## Example Problems

Copy and paste these into the UI:

### Example 1: Capacitor with Dielectric
```
A parallel-plate capacitor has plates of area 0.12 m² and a separation of 1.2 cm.
A battery charges the plates to a potential difference of 120 V and is then disconnected.
A dielectric slab of thickness 4.0 mm and dielectric constant κ = 4.8 is then placed symmetrically
between the plates.
```

### Example 2: Series Capacitors
```
A potential difference of 300 V is applied to a series connection of two capacitors
of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF.
```

### Example 3: Cylindrical Capacitor
```
A cylindrical plastic container of radius r = 0.20 m is filled to height h = 10 cm with
a conducting liquid. The exterior surface acquires a charge density of 2.0 μC/m².
```

## Troubleshooting

### "Module 'flask' not found"

Flask is not installed. Install it:
```bash
pip3 install flask flask-cors
```

### "Cannot connect to proxy"

Your network proxy is blocking pip/npm. Try:
```bash
# For pip
pip3 install --no-proxy=* flask flask-cors

# For npm
npm config delete proxy
npm config delete https-proxy
```

### "Port 5000 already in use"

Kill the process using port 5000:
```bash
lsof -ti:5000 | xargs kill -9
```

### "Port 3000 already in use"

Kill the process using port 3000:
```bash
lsof -ti:3000 | xargs kill -9
```

### "CORS error" in browser

Make sure:
1. Flask-CORS is installed: `pip3 install flask-cors`
2. API server is running on port 5000
3. No firewall blocking localhost connections

### Diagram generation fails

Check the Flask API terminal for error messages. Common issues:
- Missing Python dependencies (check requirements.txt)
- Invalid problem text (must contain physics keywords)
- Memory issues (reduce complexity)

## Architecture

```
┌──────────────┐     HTTP      ┌──────────────┐    Python     ┌───────────────────┐
│              │  ─────────>    │              │  ──────────>  │                   │
│  Next.js UI  │                │  Flask API   │               │  Unified Diagram  │
│  Port 3000   │  <─────────    │  Port 5000   │  <──────────  │  Pipeline         │
│              │     JSON       │              │     Result    │                   │
└──────────────┘                └──────────────┘               └───────────────────┘
```

## Files Created

### Backend
- `api_server.py` - Flask API wrapping UnifiedDiagramPipeline
- `requirements-api.txt` - Flask dependencies

### Frontend
- `diagram-ui/` - Next.js application
  - `app/page.tsx` - Home page
  - `app/layout.tsx` - Root layout
  - `components/DiagramGenerator.tsx` - Main UI component
  - `app/api/generate/route.ts` - API route handler
  - `package.json` - Node dependencies
  - `tsconfig.json` - TypeScript config
  - `next.config.js` - Next.js config
  - `tailwind.config.js` - Tailwind CSS config

### Scripts
- `start_ui.sh` - Automated startup script

### Documentation
- `README_UI.md` - Detailed documentation
- `SETUP_UI.md` - This file

## Production Deployment

### Backend (Flask)

Use Gunicorn for production:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### Frontend (Next.js)

Build and run:
```bash
cd diagram-ui
npm run build
npm start
```

Or deploy to Vercel:
```bash
npm install -g vercel
vercel deploy
```

## Next Steps

After setup, you can:

1. **Test with example problems** - See if diagrams generate correctly
2. **Customize styling** - Edit `diagram-ui/app/globals.css` and Tailwind config
3. **Add features** - Extend `DiagramGenerator.tsx` with:
   - Save/export diagrams
   - Diagram history
   - Problem templates
   - Batch generation
4. **Deploy to production** - Use the production deployment instructions above

## Support

For issues or questions:
1. Check console logs in browser (F12)
2. Check Flask API terminal output
3. Review error messages
4. Ensure all dependencies installed

## Dependencies

### Python (Backend)
- flask >= 3.0.0
- flask-cors >= 4.0.0
- All dependencies from requirements.txt

### Node.js (Frontend)
- next >= 14.0.0
- react >= 18.2.0
- react-dom >= 18.2.0
- typescript >= 5.0.0
- tailwindcss >= 3.3.0

## Environment Variables

Create `diagram-ui/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
```

For production, update to your deployed API URL.

---

Generated with Claude Code on November 10, 2025
