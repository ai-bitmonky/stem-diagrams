/**
 * Interactive Diagram Editor - JavaScript
 * ========================================
 *
 * Features:
 * - Drag-and-drop component placement
 * - Component selection and editing
 * - Connection management
 * - Save/Load functionality
 * - Real-time SVG rendering
 * - Integration with backend API
 */

// Global state
const EditorState = {
    currentTool: 'select',
    selectedObject: null,
    scene: {
        id: 'editor_scene',
        domain: 'electrical',
        diagram_type: 'circuit',
        title: 'Interactive Diagram',
        canvas_width: 1200,
        canvas_height: 800,
        objects: [],
        relationships: []
    },
    zoom: 1.0,
    nextObjectId: 1,
    draggedComponent: null,
    isDragging: false,
    dragOffset: { x: 0, y: 0 },
    connectionStart: null
};

// Component dimensions
const COMPONENT_SIZES = {
    resistor: { width: 80, height: 40 },
    capacitor: { width: 80, height: 60 },
    inductor: { width: 80, height: 50 },
    battery: { width: 80, height: 50 },
    ground: { width: 60, height: 40 },
    switch: { width: 70, height: 40 },
    wire: { width: 100, height: 2 },
    node: { width: 10, height: 10 }
};

// Initialize editor on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎨 Interactive Diagram Editor loaded');
    initializeDragAndDrop();
    initializeCanvasEvents();
    updateObjectCount();
});

// ========================================
// Drag and Drop
// ========================================

function initializeDragAndDrop() {
    const componentItems = document.querySelectorAll('.component-item');

    componentItems.forEach(item => {
        item.addEventListener('dragstart', handleDragStart);
        item.addEventListener('dragend', handleDragEnd);
    });

    const canvas = document.getElementById('canvas');
    canvas.addEventListener('dragover', handleDragOver);
    canvas.addEventListener('drop', handleDrop);
}

function handleDragStart(e) {
    const componentType = e.target.closest('.component-item').dataset.type;
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('componentType', componentType);
    console.log('Drag started:', componentType);
}

function handleDragEnd(e) {
    console.log('Drag ended');
}

function handleDragOver(e) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
}

function handleDrop(e) {
    e.preventDefault();

    const componentType = e.dataTransfer.getData('componentType');
    if (!componentType) return;

    // Get drop position relative to canvas
    const canvas = document.getElementById('canvas');
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    console.log(`Dropped ${componentType} at (${x}, ${y})`);

    // Create component
    createComponent(componentType, x, y);
}

// ========================================
// Component Management
// ========================================

function createComponent(type, x, y) {
    const size = COMPONENT_SIZES[type] || { width: 80, height: 40 };

    const component = {
        id: `obj_${EditorState.nextObjectId++}`,
        object_type: type.toUpperCase(),
        position: { x: x, y: y, z: 0 },
        dimensions: { width: size.width, height: size.height, depth: 0 },
        label: `${type.charAt(0).toUpperCase() + type.slice(1)}_${EditorState.nextObjectId - 1}`,
        properties: {},
        style: {}
    };

    EditorState.scene.objects.push(component);
    renderComponent(component);
    updateObjectCount();

    console.log('Created component:', component);
}

function renderComponent(component) {
    const componentsLayer = document.getElementById('components-layer');

    // Create SVG group for component
    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    group.setAttribute('id', component.id);
    group.setAttribute('class', 'component');
    group.setAttribute('transform', `translate(${component.position.x}, ${component.position.y})`);
    group.setAttribute('data-component-id', component.id);

    // Create visual representation based on type
    const visual = createComponentVisual(component);
    group.appendChild(visual);

    // Add label
    const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    label.setAttribute('x', 0);
    label.setAttribute('y', component.dimensions.height / 2 + 20);
    label.setAttribute('text-anchor', 'middle');
    label.setAttribute('font-size', '12');
    label.setAttribute('font-weight', 'bold');
    label.setAttribute('fill', '#333');
    label.textContent = component.label;
    group.appendChild(label);

    // Add event listeners
    group.addEventListener('mousedown', handleComponentMouseDown);
    group.addEventListener('click', handleComponentClick);

    componentsLayer.appendChild(group);
}

function createComponentVisual(component) {
    const type = component.object_type.toLowerCase();
    const w = component.dimensions.width;
    const h = component.dimensions.height;

    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');

    switch (type) {
        case 'resistor':
            // Zigzag pattern for resistor
            const resistorPath = `M ${-w/2} 0 L ${-w/3} ${-h/2} L ${-w/6} ${h/2} L ${w/6} ${-h/2} L ${w/3} ${h/2} L ${w/2} 0`;
            const resistor = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            resistor.setAttribute('d', resistorPath);
            resistor.setAttribute('stroke', '#ff6b6b');
            resistor.setAttribute('stroke-width', '3');
            resistor.setAttribute('fill', 'none');
            group.appendChild(resistor);
            break;

        case 'capacitor':
            // Two parallel plates
            const plate1 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            plate1.setAttribute('x1', -5);
            plate1.setAttribute('y1', -h/2);
            plate1.setAttribute('x2', -5);
            plate1.setAttribute('y2', h/2);
            plate1.setAttribute('stroke', '#4ecdc4');
            plate1.setAttribute('stroke-width', '4');
            group.appendChild(plate1);

            const plate2 = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            plate2.setAttribute('x1', 5);
            plate2.setAttribute('y1', -h/2);
            plate2.setAttribute('x2', 5);
            plate2.setAttribute('y2', h/2);
            plate2.setAttribute('stroke', '#4ecdc4');
            plate2.setAttribute('stroke-width', '4');
            group.appendChild(plate2);
            break;

        case 'inductor':
            // Coil pattern
            const coilPath = `M ${-w/2} 0 C ${-w/2} ${-h/2} ${-w/4} ${-h/2} ${-w/4} 0 C ${-w/4} ${h/2} 0 ${h/2} 0 0 C 0 ${-h/2} ${w/4} ${-h/2} ${w/4} 0 C ${w/4} ${h/2} ${w/2} ${h/2} ${w/2} 0`;
            const inductor = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            inductor.setAttribute('d', coilPath);
            inductor.setAttribute('stroke', '#95a5a6');
            inductor.setAttribute('stroke-width', '3');
            inductor.setAttribute('fill', 'none');
            group.appendChild(inductor);
            break;

        case 'battery':
            // Long and short plates
            const longPlate = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            longPlate.setAttribute('x1', -10);
            longPlate.setAttribute('y1', -h/2);
            longPlate.setAttribute('x2', -10);
            longPlate.setAttribute('y2', h/2);
            longPlate.setAttribute('stroke', '#e74c3c');
            longPlate.setAttribute('stroke-width', '4');
            group.appendChild(longPlate);

            const shortPlate = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            shortPlate.setAttribute('x1', 10);
            shortPlate.setAttribute('y1', -h/3);
            shortPlate.setAttribute('x2', 10);
            shortPlate.setAttribute('y2', h/3);
            shortPlate.setAttribute('stroke', '#e74c3c');
            shortPlate.setAttribute('stroke-width', '4');
            group.appendChild(shortPlate);
            break;

        case 'ground':
            // Ground symbol
            const groundPath = `M 0 ${-h/2} L 0 0 M ${-w/3} 0 L ${w/3} 0 M ${-w/4} ${h/4} L ${w/4} ${h/4} M ${-w/6} ${h/2} L ${w/6} ${h/2}`;
            const ground = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            ground.setAttribute('d', groundPath);
            ground.setAttribute('stroke', '#34495e');
            ground.setAttribute('stroke-width', '3');
            group.appendChild(ground);
            break;

        case 'switch':
            // Switch symbol
            const switchBase = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            switchBase.setAttribute('cx', -w/3);
            switchBase.setAttribute('cy', 0);
            switchBase.setAttribute('r', 4);
            switchBase.setAttribute('fill', '#34495e');
            group.appendChild(switchBase);

            const switchArm = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            switchArm.setAttribute('x1', -w/3);
            switchArm.setAttribute('y1', 0);
            switchArm.setAttribute('x2', w/3);
            switchArm.setAttribute('y2', -h/2);
            switchArm.setAttribute('stroke', '#34495e');
            switchArm.setAttribute('stroke-width', '3');
            group.appendChild(switchArm);

            const switchEnd = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            switchEnd.setAttribute('cx', w/3);
            switchEnd.setAttribute('cy', 0);
            switchEnd.setAttribute('r', 4);
            switchEnd.setAttribute('fill', '#34495e');
            group.appendChild(switchEnd);
            break;

        default:
            // Default: rectangle
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', -w/2);
            rect.setAttribute('y', -h/2);
            rect.setAttribute('width', w);
            rect.setAttribute('height', h);
            rect.setAttribute('fill', '#ecf0f1');
            rect.setAttribute('stroke', '#95a5a6');
            rect.setAttribute('stroke-width', '2');
            group.appendChild(rect);
            break;
    }

    return group;
}

// ========================================
// Canvas Events
// ========================================

function initializeCanvasEvents() {
    const canvas = document.getElementById('canvas');
    canvas.addEventListener('mousemove', handleCanvasMouseMove);
    canvas.addEventListener('mouseup', handleCanvasMouseUp);
}

function handleComponentMouseDown(e) {
    if (EditorState.currentTool === 'select') {
        e.stopPropagation();
        EditorState.isDragging = true;

        const componentId = e.currentTarget.dataset.componentId;
        const component = EditorState.scene.objects.find(obj => obj.id === componentId);

        if (component) {
            const rect = document.getElementById('canvas').getBoundingClientRect();
            EditorState.dragOffset = {
                x: e.clientX - rect.left - component.position.x,
                y: e.clientY - rect.top - component.position.y
            };
        }
    }
}

function handleCanvasMouseMove(e) {
    if (EditorState.isDragging && EditorState.selectedObject) {
        const canvas = document.getElementById('canvas');
        const rect = canvas.getBoundingClientRect();

        const newX = e.clientX - rect.left - EditorState.dragOffset.x;
        const newY = e.clientY - rect.top - EditorState.dragOffset.y;

        // Update component position
        EditorState.selectedObject.position.x = newX;
        EditorState.selectedObject.position.y = newY;

        // Update visual
        const group = document.getElementById(EditorState.selectedObject.id);
        if (group) {
            group.setAttribute('transform', `translate(${newX}, ${newY})`);
        }

        // Update properties panel
        updatePropertiesPanel();
    }
}

function handleCanvasMouseUp(e) {
    EditorState.isDragging = false;
}

function handleComponentClick(e) {
    e.stopPropagation();

    const componentId = e.currentTarget.dataset.componentId;
    const component = EditorState.scene.objects.find(obj => obj.id === componentId);

    if (component) {
        selectComponent(component);
    }
}

function selectComponent(component) {
    // Deselect previous
    if (EditorState.selectedObject) {
        const prevGroup = document.getElementById(EditorState.selectedObject.id);
        if (prevGroup) {
            prevGroup.classList.remove('selected');
        }
    }

    // Select new
    EditorState.selectedObject = component;
    const group = document.getElementById(component.id);
    if (group) {
        group.classList.add('selected');
    }

    // Update properties panel
    updatePropertiesPanel();
}

// ========================================
// Properties Panel
// ========================================

function updatePropertiesPanel() {
    const noSelection = document.getElementById('no-selection');
    const propertiesContent = document.getElementById('properties-content');

    if (!EditorState.selectedObject) {
        noSelection.style.display = 'block';
        propertiesContent.style.display = 'none';
        return;
    }

    noSelection.style.display = 'none';
    propertiesContent.style.display = 'flex';

    const obj = EditorState.selectedObject;

    document.getElementById('prop-id').value = obj.id;
    document.getElementById('prop-type').value = obj.object_type;
    document.getElementById('prop-label').value = obj.label;
    document.getElementById('prop-x').value = Math.round(obj.position.x);
    document.getElementById('prop-y').value = Math.round(obj.position.y);
    document.getElementById('prop-width').value = obj.dimensions.width;
    document.getElementById('prop-height').value = obj.dimensions.height;
    document.getElementById('prop-rotation').value = obj.properties.rotation || 0;
}

function updateProperty(property, value) {
    if (!EditorState.selectedObject) return;

    const obj = EditorState.selectedObject;

    switch (property) {
        case 'label':
            obj.label = value;
            // Update label text
            const labelElement = document.querySelector(`#${obj.id} text`);
            if (labelElement) {
                labelElement.textContent = value;
            }
            break;
        case 'x':
            obj.position.x = parseFloat(value);
            updateComponentTransform(obj);
            break;
        case 'y':
            obj.position.y = parseFloat(value);
            updateComponentTransform(obj);
            break;
        case 'width':
            obj.dimensions.width = parseFloat(value);
            rerenderComponent(obj);
            break;
        case 'height':
            obj.dimensions.height = parseFloat(value);
            rerenderComponent(obj);
            break;
        case 'rotation':
            if (!obj.properties) obj.properties = {};
            obj.properties.rotation = parseFloat(value);
            updateComponentTransform(obj);
            break;
    }
}

function updateComponentTransform(component) {
    const group = document.getElementById(component.id);
    if (group) {
        const rotation = component.properties?.rotation || 0;
        group.setAttribute('transform',
            `translate(${component.position.x}, ${component.position.y}) rotate(${rotation})`);
    }
}

function rerenderComponent(component) {
    // Remove old component
    const oldGroup = document.getElementById(component.id);
    if (oldGroup) {
        oldGroup.remove();
    }

    // Render new component
    renderComponent(component);

    // Re-select
    selectComponent(component);
}

// ========================================
// Tools
// ========================================

function selectTool(tool) {
    EditorState.currentTool = tool;

    // Update UI
    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tool="${tool}"]`).classList.add('active');

    console.log('Selected tool:', tool);
}

function deleteSelected() {
    if (!EditorState.selectedObject) return;

    const objectId = EditorState.selectedObject.id;

    // Remove from scene
    EditorState.scene.objects = EditorState.scene.objects.filter(obj => obj.id !== objectId);

    // Remove from DOM
    const group = document.getElementById(objectId);
    if (group) {
        group.remove();
    }

    // Clear selection
    EditorState.selectedObject = null;
    updatePropertiesPanel();
    updateObjectCount();

    console.log('Deleted object:', objectId);
}

function duplicateSelected() {
    if (!EditorState.selectedObject) return;

    const original = EditorState.selectedObject;
    const duplicate = JSON.parse(JSON.stringify(original));

    // New ID and position
    duplicate.id = `obj_${EditorState.nextObjectId++}`;
    duplicate.position.x += 50;
    duplicate.position.y += 50;
    duplicate.label = duplicate.label.replace(/\d+$/, EditorState.nextObjectId - 1);

    // Add to scene
    EditorState.scene.objects.push(duplicate);
    renderComponent(duplicate);
    selectComponent(duplicate);
    updateObjectCount();

    console.log('Duplicated object:', duplicate);
}

// ========================================
// Zoom Controls
// ========================================

function zoomIn() {
    EditorState.zoom = Math.min(EditorState.zoom + 0.1, 3.0);
    updateZoom();
}

function zoomOut() {
    EditorState.zoom = Math.max(EditorState.zoom - 0.1, 0.3);
    updateZoom();
}

function resetZoom() {
    EditorState.zoom = 1.0;
    updateZoom();
}

function updateZoom() {
    const diagramGroup = document.getElementById('diagram-group');
    diagramGroup.setAttribute('transform', `scale(${EditorState.zoom})`);

    const zoomLevel = document.getElementById('zoom-level');
    zoomLevel.textContent = Math.round(EditorState.zoom * 100) + '%';
}

// ========================================
// Auto Layout
// ========================================

async function autoLayout() {
    showLoading('Optimizing layout...');

    try {
        const response = await fetch('/api/editor/optimize_layout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                scene: EditorState.scene,
                enable_force_directed: true
            })
        });

        const result = await response.json();

        if (result.success) {
            EditorState.scene = result.scene;
            reloadCanvas();
            console.log('Layout optimized');
        } else {
            alert('Error optimizing layout: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error optimizing layout: ' + error.message);
    }

    hideLoading();
}

// ========================================
// Validation
// ========================================

async function validateDiagram() {
    showLoading('Validating diagram...');

    try {
        const response = await fetch('/api/editor/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scene: EditorState.scene })
        });

        const result = await response.json();

        if (result.success) {
            displayQualityScore(result);
            console.log('Validation complete:', result);
        } else {
            alert('Error validating: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error validating: ' + error.message);
    }

    hideLoading();
}

function displayQualityScore(result) {
    const scoreSection = document.getElementById('quality-score');
    scoreSection.style.display = 'block';

    document.getElementById('score-value').textContent = Math.round(result.quality_score);
    document.getElementById('score-layout').textContent = Math.round(result.layout_score);
    document.getElementById('score-connectivity').textContent = Math.round(result.connectivity_score);
    document.getElementById('score-style').textContent = Math.round(result.style_score);
    document.getElementById('score-physics').textContent = Math.round(result.physics_score);
}

// ========================================
// Generate from Text
// ========================================

function generateFromText() {
    openModal('generate-modal');
}

async function generateDiagram() {
    const problemText = document.getElementById('generate-text').value.trim();
    if (!problemText) {
        alert('Please enter problem text');
        return;
    }

    const enableLayout = document.getElementById('opt-layout').checked;
    const enableValidation = document.getElementById('opt-validation').checked;
    const enableForceDirected = document.getElementById('opt-force-directed').checked;
    const style = document.getElementById('render-style').value;

    closeModal('generate-modal');
    showLoading('Generating diagram...');

    try {
        const response = await fetch('/api/editor/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                problem: problemText,
                style: style,
                enable_layout_optimization: enableLayout,
                enable_validation: enableValidation,
                enable_force_directed: enableForceDirected
            })
        });

        const result = await response.json();

        if (result.success) {
            EditorState.scene = result.scene;
            EditorState.nextObjectId = result.scene.objects.length + 1;
            reloadCanvas();

            if (result.quality_score) {
                displayQualityScore({ quality_score: result.quality_score });
            }

            console.log('Diagram generated successfully');
        } else {
            alert('Error generating diagram: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error generating diagram: ' + error.message);
    }

    hideLoading();
}

// ========================================
// Save/Load/Export
// ========================================

async function saveScene() {
    const filename = prompt('Enter filename:', 'my_diagram');
    if (!filename) return;

    showLoading('Saving...');

    try {
        const response = await fetch('/api/editor/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                scene: EditorState.scene,
                filename: filename
            })
        });

        const result = await response.json();

        if (result.success) {
            alert('Saved successfully to: ' + result.filepath);
        } else {
            alert('Error saving: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error saving: ' + error.message);
    }

    hideLoading();
}

async function loadScene() {
    const filename = prompt('Enter filename to load (without extension):');
    if (!filename) return;

    showLoading('Loading...');

    try {
        const response = await fetch(`/api/editor/load?filename=${encodeURIComponent(filename)}`);
        const result = await response.json();

        if (result.success) {
            EditorState.scene = result.scene;
            EditorState.nextObjectId = result.scene.objects.length + 1;
            reloadCanvas();
            alert('Loaded successfully');
        } else {
            alert('Error loading: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error loading: ' + error.message);
    }

    hideLoading();
}

async function exportScene() {
    const filename = prompt('Enter filename for export:', 'diagram');
    if (!filename) return;

    showLoading('Exporting...');

    try {
        const response = await fetch('/api/editor/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                scene: EditorState.scene,
                filename: filename,
                style: 'modern'
            })
        });

        const result = await response.json();

        if (result.success) {
            alert('Exported successfully to: ' + result.filepath);
        } else {
            alert('Error exporting: ' + result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error exporting: ' + error.message);
    }

    hideLoading();
}

// ========================================
// UI Utilities
// ========================================

function reloadCanvas() {
    // Clear canvas
    document.getElementById('components-layer').innerHTML = '';
    document.getElementById('connections-layer').innerHTML = '';

    // Render all objects
    EditorState.scene.objects.forEach(obj => {
        renderComponent(obj);
    });

    updateObjectCount();
}

function updateObjectCount() {
    const count = EditorState.scene.objects.length;
    document.getElementById('object-count').textContent = `${count} object${count !== 1 ? 's' : ''}`;
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('active');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('active');
}

function showLoading(message) {
    document.getElementById('loading-message').textContent = message;
    openModal('loading-modal');
}

function hideLoading() {
    closeModal('loading-modal');
}

// Close modals on background click
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});
