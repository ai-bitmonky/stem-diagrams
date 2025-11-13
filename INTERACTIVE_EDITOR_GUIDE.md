# Interactive Diagram Editor - User Guide

## Overview

The Interactive Diagram Editor is a web-based tool for creating and editing STEM diagrams with a drag-and-drop interface. It provides professional-quality diagram creation with real-time editing, automatic layout optimization, and quality validation.

## Features

### 🎨 **Visual Editing**
- Drag-and-drop component placement from palette
- Real-time SVG rendering
- Interactive component selection and editing
- Visual feedback for selection and hover states

### 🛠️ **Tools**
- **Select Tool**: Click and drag to move components
- **Connect Tool**: Draw connections between components
- **Delete Tool**: Remove components and connections

### 📐 **Auto Layout**
- Force-directed graph layout algorithm
- Automatic collision detection and avoidance
- Grid snapping for professional alignment
- One-click layout optimization

### ✅ **Quality Validation**
- Real-time diagram validation
- Quality scoring (0-100)
- Component scores for:
  - Layout quality
  - Connectivity
  - Style consistency
  - Physics accuracy

### 🤖 **AI-Powered Generation**
- Generate diagrams from natural language text
- Automatic component extraction and placement
- Support for electrical, chemistry, biology, and physics domains
- Multiple rendering styles (Classic, Modern, 3D)

### 💾 **Save/Load/Export**
- Save diagrams to JSON format
- Load previously saved diagrams
- Export to SVG format
- Persistent storage on server

## Getting Started

### 1. Start the Web Server

```bash
python web_interface.py
```

The server will start on `http://localhost:5000`

### 2. Access the Editor

Open your browser to:
```
http://localhost:5000/editor
```

### 3. Create Your First Diagram

#### Option A: Generate from Text

1. Click the **"Generate from Text"** button in the header
2. Enter a problem description, for example:
   ```
   A series circuit with a 12V battery, 100Ω resistor, and 10μF capacitor
   ```
3. Choose options:
   - Enable layout optimization
   - Enable validation
   - Use force-directed layout
   - Select rendering style (Modern, Classic, 3D)
4. Click **"Generate"**
5. The diagram will appear on the canvas

#### Option B: Manual Creation

1. From the **Component Palette** (left sidebar), drag components onto the canvas
2. Available components:
   - **Electrical**: Resistor, Capacitor, Inductor, Battery, Ground, Switch
   - **Connections**: Wire, Node
3. Use the **Select Tool** to move components
4. Click **"Auto Layout"** to optimize positioning
5. Click **"Validate"** to check quality

## User Interface

### Header
- **Generate from Text**: AI-powered diagram generation
- **Save**: Save current diagram to file
- **Load**: Load previously saved diagram
- **Export SVG**: Export diagram as SVG file

### Left Sidebar - Component Palette
- **Components**: Drag-and-drop component library
  - Electrical components with icons
  - Connection elements
- **Tools**: Select, Connect, Delete

### Center - Canvas
- **Toolbar**:
  - Zoom In/Out/Reset
  - Auto Layout: Optimize component positioning
  - Validate: Check diagram quality
  - Status: Shows zoom level and object count
- **Canvas**: Main editing area with grid background
  - Drag components to reposition
  - Click to select
  - Visual grid for alignment

### Right Sidebar - Properties Panel
- **Properties**: Edit selected component
  - ID (read-only)
  - Type (read-only)
  - Label (editable)
  - Position X, Y
  - Width, Height
  - Rotation
- **Actions**:
  - Delete selected component
  - Duplicate selected component
- **Quality Score**: (after validation)
  - Overall score (0-100)
  - Breakdown by category

## Keyboard Shortcuts

- **Drag Component**: Click and drag
- **Select Multiple**: (coming soon)
- **Delete**: Delete key (after selecting)
- **Undo/Redo**: (coming soon)

## Workflow Examples

### Example 1: Creating an RC Circuit

1. **Generate from text**:
   ```
   A series RC circuit with a 9V battery, 470Ω resistor, and 100μF capacitor
   ```

2. **Refine manually**:
   - Click on resistor to select
   - Adjust position using properties panel
   - Change label to "R1 = 470Ω"

3. **Optimize**:
   - Click "Auto Layout" to optimize positioning
   - Click "Validate" to check quality

4. **Export**:
   - Click "Export SVG"
   - Enter filename: "rc_circuit"

### Example 2: Manual Circuit Creation

1. **Add components**:
   - Drag Battery from palette to canvas
   - Drag Resistor from palette
   - Drag Capacitor from palette
   - Drag Ground symbol

2. **Position components**:
   - Click "Auto Layout" for automatic positioning
   - Or manually drag to desired positions

3. **Edit properties**:
   - Select battery
   - Change label to "V1 = 9V"
   - Repeat for other components

4. **Validate**:
   - Click "Validate"
   - Review quality score
   - Fix any issues

5. **Save**:
   - Click "Save"
   - Enter filename: "my_circuit"

## API Endpoints

The editor uses RESTful API endpoints for backend integration:

### `/api/editor/generate` [POST]
Generate diagram from text description

**Request:**
```json
{
  "problem": "A circuit with a battery and resistor",
  "style": "modern",
  "enable_layout_optimization": true,
  "enable_validation": true,
  "enable_force_directed": false
}
```

**Response:**
```json
{
  "success": true,
  "svg": "<svg>...</svg>",
  "scene": {...},
  "quality_score": 92.5
}
```

### `/api/editor/validate` [POST]
Validate diagram and get quality score

**Request:**
```json
{
  "scene": {...}
}
```

**Response:**
```json
{
  "success": true,
  "quality_score": 92.5,
  "layout_score": 95,
  "connectivity_score": 90,
  "style_score": 92,
  "physics_score": 93,
  "issues": [...]
}
```

### `/api/editor/optimize_layout` [POST]
Optimize scene layout automatically

**Request:**
```json
{
  "scene": {...},
  "enable_force_directed": true
}
```

**Response:**
```json
{
  "success": true,
  "scene": {...}
}
```

### `/api/editor/save` [POST]
Save scene to file

**Request:**
```json
{
  "scene": {...},
  "filename": "my_diagram"
}
```

**Response:**
```json
{
  "success": true,
  "filepath": "/path/to/my_diagram.json"
}
```

### `/api/editor/load` [GET]
Load scene from file

**Query:** `?filename=my_diagram`

**Response:**
```json
{
  "success": true,
  "scene": {...}
}
```

### `/api/editor/export` [POST]
Export diagram to SVG

**Request:**
```json
{
  "scene": {...},
  "filename": "diagram",
  "style": "modern"
}
```

**Response:**
```json
{
  "success": true,
  "filepath": "/path/to/diagram.svg"
}
```

## Technical Details

### Architecture

```
┌─────────────────────────────────────────────┐
│           Web Browser (Client)              │
│  ┌────────────┐  ┌────────────┐            │
│  │  HTML/CSS  │  │ JavaScript │            │
│  │  editor.   │  │  editor.js │            │
│  │   html     │  │           │            │
│  └────────────┘  └────────────┘            │
└───────────────────┬─────────────────────────┘
                    │ REST API
┌───────────────────▼─────────────────────────┐
│         Flask Web Server (Backend)          │
│  ┌────────────────────────────────────┐    │
│  │     Enhanced Pipeline              │    │
│  │  - NLP Extraction                  │    │
│  │  - Scene Building                  │    │
│  │  - Layout Optimization             │    │
│  │  - Validation & Refinement         │    │
│  │  - SVG Rendering                   │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### Technologies Used

**Frontend:**
- HTML5 for structure
- CSS3 for styling (Flexbox, Grid, Animations)
- Vanilla JavaScript (ES6+) for logic
- SVG for diagram rendering

**Backend:**
- Flask web framework
- Enhanced NLP Pipeline
- Intelligent Layout Engine
- Validation & Refinement Layer
- Enhanced Component Library

### File Structure

```
web/
├── templates/
│   └── editor.html          # Main editor UI
├── static/
│   ├── css/
│   │   └── editor.css       # Editor styling
│   └── js/
│       └── editor.js        # Editor logic
web_interface.py             # Flask server with API routes
output/
└── web_editor/              # Saved diagrams and exports
```

## Troubleshooting

### Editor Not Loading
**Problem**: Editor page shows error or doesn't load

**Solution**:
1. Check if Enhanced Pipeline is installed:
   ```python
   from core.enhanced_nlp_pipeline import EnhancedNLPPipeline
   ```
2. Verify Flask server is running
3. Check browser console for errors

### Generate from Text Not Working
**Problem**: Diagram generation fails or produces empty result

**Solution**:
1. Check problem text format
2. Ensure Enhanced Pipeline dependencies are installed
3. Review server logs for errors
4. Try a simpler example first

### Components Not Appearing
**Problem**: Dragged components don't appear on canvas

**Solution**:
1. Check JavaScript console for errors
2. Verify component type is supported
3. Try refreshing the page
4. Check browser compatibility (Chrome, Firefox, Safari recommended)

### Quality Score Shows 0
**Problem**: Validation returns score of 0

**Solution**:
1. Ensure diagram has components
2. Check if components have proper relationships
3. Try Auto Layout before validating
4. Review validation issues in properties panel

## Browser Compatibility

**Supported Browsers:**
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

**Not Supported:**
- ❌ Internet Explorer (any version)
- ❌ Mobile browsers (responsive design coming soon)

## Performance

**Recommended Limits:**
- Maximum components: 50 (for optimal performance)
- Maximum connections: 100
- Canvas size: Up to 2000x2000px

**Performance Tips:**
- Use Auto Layout instead of manual positioning for complex diagrams
- Disable force-directed layout for diagrams with >30 components
- Save frequently when working with large diagrams

## Future Enhancements

Planned features for future releases:

- 🔄 Undo/Redo functionality
- 📱 Mobile responsive design
- 🔗 Connection drawing tool (visual wire routing)
- 📋 Multi-select and bulk operations
- ⌨️ Keyboard shortcuts
- 🎨 Custom component styling
- 📤 Export to PNG/PDF formats
- 🌐 Real-time collaboration
- 📚 Component library expansion
- 🔍 Search and filter components
- 📊 Diagram analytics and statistics

## Support

For issues, questions, or feature requests:

1. Check this guide first
2. Review the main documentation
3. Check the GitHub issues
4. Contact the development team

## License

Part of the Universal STEM Diagram Generator project.
Date: November 5, 2025

---

**Happy Diagramming! 🎨✨**
