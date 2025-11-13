# Deployment Guide - Interactive Diagram Editor

## Quick Start

### Prerequisites

Ensure you have Python 3.8+ installed:

```bash
python3 --version
```

### Installation

1. **Install Flask and dependencies:**

```bash
pip install flask flask-cors
```

2. **Install Enhanced Pipeline dependencies (if not already installed):**

```bash
pip install spacy quantulum3
python -m spacy download en_core_web_sm
```

3. **Verify installation:**

```bash
python3 -c "import flask; print('Flask:', flask.__version__)"
python3 -c "import spacy; print('spaCy:', spacy.__version__)"
```

### Start the Server

From the project root directory:

```bash
python web_interface.py
```

You should see:

```
======================================================================
STEM DIAGRAM GENERATOR - WEB INTERFACE
======================================================================

🌐 Starting web server...
📍 Main interface: http://localhost:5000
🎨 Interactive Editor: http://localhost:5000/editor
⚡ Press Ctrl+C to stop

======================================================================

 * Running on http://0.0.0.0:5000
```

### Access the Editor

Open your browser to:

```
http://localhost:5000/editor
```

You should see the Interactive Diagram Editor interface with:
- Component palette on the left
- Canvas in the center
- Properties panel on the right

## Quick Test

### Test 1: Generate from Text

1. Click **"Generate from Text"** button
2. Enter:
   ```
   A circuit with a 9V battery and 100Ω resistor
   ```
3. Click **"Generate"**
4. Verify diagram appears on canvas

### Test 2: Manual Component Placement

1. From the palette, drag **Battery** onto the canvas
2. Drag **Resistor** onto the canvas
3. Click one component to select it
4. Verify properties appear in the right panel

### Test 3: Auto Layout

1. With components on canvas, click **"Auto Layout"**
2. Verify components reposition automatically

### Test 4: Validation

1. Click **"Validate"**
2. Verify quality score appears in properties panel

### Test 5: Save/Load

1. Click **"Save"**, enter filename: `test_circuit`
2. Refresh the page
3. Click **"Load"**, enter filename: `test_circuit`
4. Verify diagram reloads

## Troubleshooting

### Issue: ModuleNotFoundError: No module named 'flask'

**Solution:**
```bash
pip install flask flask-cors
```

### Issue: Enhanced Pipeline not available

**Solution:**
```bash
pip install spacy quantulum3
python -m spacy download en_core_web_sm
```

### Issue: Port 5000 already in use

**Solution:**
Edit `web_interface.py` line 941:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

### Issue: Editor page shows 503 error

**Cause:** Enhanced Pipeline dependencies not installed

**Solution:** Install all dependencies as shown above

### Issue: Components not appearing when dragged

**Solution:**
1. Check browser console (F12) for errors
2. Try refreshing the page
3. Ensure JavaScript is enabled
4. Try a different browser (Chrome/Firefox recommended)

## Production Deployment

For production deployment, use a production WSGI server:

### Option 1: Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_interface:app
```

### Option 2: Waitress (Windows)

```bash
pip install waitress
waitress-serve --listen=0.0.0.0:5000 web_interface:app
```

### Security Considerations

1. **Disable Debug Mode:**
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

2. **Set Secret Key:**
   ```python
   app.config['SECRET_KEY'] = 'your-secret-key-here'
   ```

3. **Enable HTTPS** (use reverse proxy like Nginx)

4. **Rate Limiting** (consider Flask-Limiter)

5. **Input Validation** (already implemented)

## File Permissions

Ensure the following directories are writable:

```bash
chmod 755 web/
chmod 755 web/static/
chmod 755 web/templates/
chmod 755 output/
chmod 755 output/web_editor/
```

## Environment Variables (Optional)

You can configure the application using environment variables:

```bash
export FLASK_ENV=production
export FLASK_APP=web_interface.py
export OUTPUT_DIR=output/web_editor
```

## Monitoring

To monitor the application:

```bash
# Check if running
ps aux | grep web_interface

# View logs (if using systemd)
journalctl -u diagram-editor -f

# Check port
netstat -an | grep 5000
```

## Backup

Regularly backup the output directory:

```bash
tar -czf backup_$(date +%Y%m%d).tar.gz output/web_editor/
```

## Updates

To update the application:

```bash
# Pull latest changes (if using git)
git pull

# Restart server
# (Stop with Ctrl+C and restart)
python web_interface.py
```

## Support

For issues or questions:

1. Check [INTERACTIVE_EDITOR_GUIDE.md](INTERACTIVE_EDITOR_GUIDE.md)
2. Review [COMPLETE_IMPLEMENTATION_SUMMARY.md](COMPLETE_IMPLEMENTATION_SUMMARY.md)
3. Check project documentation at `index.html`

## Verification Checklist

Before going live, verify:

- [ ] Flask installed and working
- [ ] Enhanced Pipeline dependencies installed
- [ ] Web server starts without errors
- [ ] Editor page loads successfully
- [ ] Generate from text works
- [ ] Component drag-and-drop works
- [ ] Save/Load functionality works
- [ ] Export to SVG works
- [ ] All API endpoints respond
- [ ] Browser console shows no errors

## Quick Reference

**Start Server:**
```bash
python web_interface.py
```

**Access Main Interface:**
```
http://localhost:5000
```

**Access Editor:**
```
http://localhost:5000/editor
```

**Health Check:**
```
http://localhost:5000/health
```

**API Endpoints:**
- POST `/api/editor/generate` - Generate diagram
- POST `/api/editor/validate` - Validate quality
- POST `/api/editor/optimize_layout` - Optimize layout
- POST `/api/editor/save` - Save diagram
- GET `/api/editor/load` - Load diagram
- POST `/api/editor/export` - Export SVG

---

**Happy Deploying! 🚀**
