"""
Interactive Web Interface for Unified Diagram Generator
=======================================================

Flask-based web application for generating STEM diagrams from text.

Features:
- Real-time diagram generation
- Interactive preview
- Multi-domain support
- Download SVG and JSON
- Generation statistics
- Batch processing
- Interactive diagram editor with drag-and-drop

Author: Universal Diagram Generator Team
Date: November 5, 2025
"""

from flask import Flask, render_template_string, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
from pathlib import Path
import json
from unified_diagram_generator import UnifiedDiagramGenerator

# Import UnifiedPipeline (new integrated pipeline)
try:
    from core.unified_pipeline import UnifiedPipeline, PipelineMode
    from core.llm_integration import LLMConfig, LLMProvider
    UNIFIED_PIPELINE_AVAILABLE = True
except ImportError:
    UNIFIED_PIPELINE_AVAILABLE = False
    print("⚠️  UnifiedPipeline not available - falling back to baseline generator")

# Import Enhanced Pipeline components
try:
    from core.universal_scene_format import UniversalScene
    from core.enhanced_nlp_pipeline import EnhancedNLPPipeline
    from core.advanced_scene_builder import AdvancedSceneBuilder
    from core.enhanced_component_library import EnhancedComponentLibrary
    from core.intelligent_layout_engine import IntelligentLayoutEngine
    from core.validation_refinement import DiagramValidator, DiagramRefiner
    from renderers.enhanced_svg_renderer import EnhancedSVGRenderer
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False
    print("⚠️  Enhanced Pipeline not available - editor will have limited functionality")

app = Flask(__name__,
            template_folder='web/templates',
            static_folder='web/static')
CORS(app)  # Enable CORS for API calls

# Initialize generator (legacy baseline)
generator = UnifiedDiagramGenerator(output_dir="output/web_generated")

# Initialize UnifiedPipeline instances for each mode (cached for performance)
if UNIFIED_PIPELINE_AVAILABLE:
    pipeline_fast = UnifiedPipeline(mode=PipelineMode.FAST, output_dir="output/web_generated")
    pipeline_accurate = None  # Lazy init (needs Ollama)
    pipeline_premium = None   # Lazy init (needs Ollama + VLM)
    print("✅ UnifiedPipeline FAST mode initialized")
else:
    pipeline_fast = None
    pipeline_accurate = None
    pipeline_premium = None

# Initialize Enhanced Pipeline if available
if ENHANCED_AVAILABLE:
    nlp_pipeline = EnhancedNLPPipeline()
    scene_builder = AdvancedSceneBuilder()
    layout_engine = IntelligentLayoutEngine()
    validator = DiagramValidator()
    refiner = DiagramRefiner()
    component_library = EnhancedComponentLibrary()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>STEM Diagram Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        header h1 {
            font-size: 3em;
            margin-bottom: 10px;
        }

        header p {
            font-size: 1.2em;
            opacity: 0.95;
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            padding: 40px;
        }

        .input-section, .output-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
        }

        .section-title {
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            font-weight: bold;
        }

        textarea {
            width: 100%;
            min-height: 300px;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            font-family: 'Segoe UI', sans-serif;
            resize: vertical;
            transition: border-color 0.3s;
        }

        textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }

        button {
            flex: 1;
            padding: 15px 30px;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-generate {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-generate:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }

        .btn-clear {
            background: #e0e0e0;
            color: #333;
        }

        .btn-clear:hover {
            background: #d0d0d0;
        }

        .btn-download {
            background: #27ae60;
            color: white;
        }

        .btn-download:hover {
            background: #229954;
        }

        .diagram-container {
            width: 100%;
            min-height: 400px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .diagram-container svg {
            max-width: 100%;
            height: auto;
        }

        .placeholder {
            color: #999;
            font-size: 1.2em;
            text-align: center;
        }

        .stats-section {
            margin-top: 20px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            display: none;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 15px;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 40px;
        }

        .loading.active {
            display: block;
        }

        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .example-section {
            grid-column: 1 / -1;
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            margin-top: 20px;
        }

        .example-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .example-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid transparent;
        }

        .example-card:hover {
            border-color: #667eea;
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }

        .example-title {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }

        .example-text {
            color: #666;
            font-size: 0.9em;
        }

        @media (max-width: 968px) {
            .main-content {
                grid-template-columns: 1fr;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎨 STEM Diagram Generator v2.0</h1>
            <p>Generate professional diagrams with AI-powered multi-mode pipeline</p>
            <p style="font-size: 0.9em; margin-top: 10px; opacity: 0.8;">
                Supports: Physics • Chemistry • Biology • Mathematics • Electronics
            </p>
            <p style="font-size: 0.85em; margin-top: 8px; opacity: 0.75;">
                ⚡ FAST • 🧠 ACCURATE (LLM) • 💎 PREMIUM (LLM+VLM)
            </p>
        </header>

        <div class="main-content">
            <!-- Input Section -->
            <div class="input-section">
                <div class="section-title">📝 Input</div>
                <textarea id="problemText" placeholder="Enter your problem text here...

Example:
A series circuit with a 12V battery, 100Ω resistor, and 10μF capacitor.

The system will automatically detect the domain and generate an appropriate diagram."></textarea>

                <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 10px;">
                    <label style="font-weight: bold; color: #667eea; margin-bottom: 10px; display: block;">
                        🎯 Pipeline Mode:
                    </label>
                    <select id="pipelineMode" style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; cursor: pointer;">
                        <option value="fast" selected>⚡ FAST - Keyword-based (1s, offline)</option>
                        <option value="accurate">🧠 ACCURATE - LLM-powered (5-10s, needs Ollama)</option>
                        <option value="premium">💎 PREMIUM - LLM + VLM validation (10-15s, needs Ollama + GPU)</option>
                    </select>
                    <p style="font-size: 0.85em; color: #666; margin-top: 8px; margin-bottom: 0;">
                        <strong>FAST:</strong> Uses keyword heuristics + spaCy (offline, no setup required)<br>
                        <strong>ACCURATE:</strong> Uses local LLM for better reasoning (requires Ollama)<br>
                        <strong>PREMIUM:</strong> Adds visual validation with VLM (requires Ollama + transformers)
                    </p>
                </div>

                <div class="button-group">
                    <button class="btn-generate" onclick="generateDiagram()">
                        🚀 Generate Diagram
                    </button>
                    <button class="btn-clear" onclick="clearAll()">
                        🗑️ Clear
                    </button>
                </div>
            </div>

            <!-- Output Section -->
            <div class="output-section">
                <div class="section-title">📊 Output</div>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Generating diagram...</p>
                </div>

                <div class="diagram-container" id="diagramContainer">
                    <div class="placeholder">
                        Your diagram will appear here after generation
                    </div>
                </div>

                <div class="stats-section" id="statsSection">
                    <h3 style="color: #667eea; margin-bottom: 15px;">📈 Generation Statistics</h3>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value" id="statDomain">-</div>
                            <div class="stat-label">Domain</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="statObjects">0</div>
                            <div class="stat-label">Objects</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="statTime">0s</div>
                            <div class="stat-label">Time</div>
                        </div>
                    </div>
                </div>

                <div class="button-group" style="margin-top: 20px; display: none;" id="downloadSection">
                    <button class="btn-download" onclick="downloadSVG()">
                        ⬇️ Download SVG
                    </button>
                    <button class="btn-download" onclick="downloadJSON()">
                        ⬇️ Download JSON
                    </button>
                </div>
            </div>

            <!-- Example Section -->
            <div class="example-section">
                <div class="section-title">💡 Example Problems</div>
                <div class="example-grid">
                    <div class="example-card" onclick="loadExample(0)">
                        <div class="example-title">⚡ Electronics - RC Circuit</div>
                        <div class="example-text">
                            A series circuit with a 12V battery, 100Ω resistor, and 10μF capacitor.
                        </div>
                    </div>
                    <div class="example-card" onclick="loadExample(1)">
                        <div class="example-title">🧪 Chemistry - Water Molecule</div>
                        <div class="example-text">
                            A water molecule (H₂O) consists of one oxygen atom bonded to two hydrogen atoms.
                        </div>
                    </div>
                    <div class="example-card" onclick="loadExample(2)">
                        <div class="example-title">🦠 Biology - Cell Structure</div>
                        <div class="example-text">
                            A cell with a nucleus, mitochondria, and ribosomes.
                        </div>
                    </div>
                    <div class="example-card" onclick="loadExample(3)">
                        <div class="example-title">🎯 Physics - Force Diagram</div>
                        <div class="example-text">
                            A mass m = 5 kg rests on a horizontal surface with friction coefficient μ = 0.3.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const examples = [
            "A series circuit with a 12V battery, 100Ω resistor, and 10μF capacitor. Calculate the time constant τ = RC.",
            "A water molecule (H₂O) consists of one oxygen atom bonded to two hydrogen atoms. The bond angle is approximately 104.5 degrees.",
            "A cell with a nucleus, mitochondria, and ribosomes. The nucleus contains DNA and controls cellular functions.",
            "A mass m = 5 kg rests on a horizontal surface with friction coefficient μ = 0.3. A force F = 20 N is applied horizontally."
        ];

        let currentResult = null;

        function loadExample(index) {
            document.getElementById('problemText').value = examples[index];
        }

        function clearAll() {
            document.getElementById('problemText').value = '';
            document.getElementById('diagramContainer').innerHTML = '<div class="placeholder">Your diagram will appear here after generation</div>';
            document.getElementById('statsSection').style.display = 'none';
            document.getElementById('downloadSection').style.display = 'none';
            currentResult = null;
        }

        async function generateDiagram() {
            const problemText = document.getElementById('problemText').value.trim();
            const mode = document.getElementById('pipelineMode').value;

            if (!problemText) {
                alert('Please enter a problem description');
                return;
            }

            // Show loading with mode-specific message
            const loadingMessages = {
                'fast': 'Generating diagram (FAST mode)...',
                'accurate': 'Generating diagram with LLM reasoning (ACCURATE mode)...',
                'premium': 'Generating and validating diagram (PREMIUM mode)...'
            };
            document.querySelector('#loading p').textContent = loadingMessages[mode];

            // Show loading
            document.getElementById('loading').classList.add('active');
            document.getElementById('diagramContainer').style.display = 'none';
            document.getElementById('statsSection').style.display = 'none';
            document.getElementById('downloadSection').style.display = 'none';

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        problem_text: problemText,
                        mode: mode
                    })
                });

                const result = await response.json();

                // Hide loading
                document.getElementById('loading').classList.remove('active');
                document.getElementById('diagramContainer').style.display = 'flex';

                if (result.success) {
                    // Display SVG
                    document.getElementById('diagramContainer').innerHTML = result.svg;

                    // Update stats
                    const pipelineMode = result.metadata?.pipeline_mode || mode;
                    document.getElementById('statDomain').textContent =
                        (result.metadata.domain || 'Unknown').toUpperCase();
                    document.getElementById('statObjects').textContent = result.metadata.num_objects || 0;
                    document.getElementById('statTime').textContent =
                        (result.metadata.total_time || 0).toFixed(3) + 's';

                    // Show mode badge
                    const modeBadges = {
                        'fast': '⚡ FAST',
                        'accurate': '🧠 ACCURATE',
                        'premium': '💎 PREMIUM',
                        'legacy': '📦 LEGACY'
                    };
                    document.getElementById('statDomain').textContent +=
                        ' • ' + (modeBadges[pipelineMode] || pipelineMode.toUpperCase());

                    document.getElementById('statsSection').style.display = 'block';
                    document.getElementById('downloadSection').style.display = 'flex';

                    currentResult = result;

                    // Show additional info for ACCURATE/PREMIUM modes
                    if (mode === 'accurate' || mode === 'premium') {
                        if (result.nlp_results?.llm_reasoning) {
                            console.log('LLM Reasoning:', result.nlp_results.llm_reasoning);
                        }
                    }

                    if (mode === 'premium' && result.validation?.vlm) {
                        console.log('VLM Validation:', result.validation.vlm);
                    }
                } else {
                    // Handle error with helpful hints
                    let errorMsg = result.error;
                    if (result.hint) {
                        errorMsg += `<br><br><small style="color: #e67e22;">💡 ${result.hint}</small>`;
                    }
                    document.getElementById('diagramContainer').innerHTML =
                        `<div class="placeholder" style="color: #c0392b;">
                            ❌ Error: ${errorMsg}
                        </div>`;
                }
            } catch (error) {
                document.getElementById('loading').classList.remove('active');
                document.getElementById('diagramContainer').style.display = 'flex';
                document.getElementById('diagramContainer').innerHTML =
                    `<div class="placeholder" style="color: #c0392b;">
                        ❌ Error: ${error.message}
                    </div>`;
            }
        }

        function downloadSVG() {
            if (!currentResult) return;

            const blob = new Blob([currentResult.svg], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'diagram.svg';
            a.click();
            URL.revokeObjectURL(url);
        }

        function downloadJSON() {
            if (!currentResult) return;

            const blob = new Blob([currentResult.scene_json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'scene.json';
            a.click();
            URL.revokeObjectURL(url);
        }

        // Enable enter key to generate
        document.getElementById('problemText').addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                generateDiagram();
            }
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/generate', methods=['POST'])
def api_generate():
    """API endpoint for diagram generation with mode selection"""
    global pipeline_accurate, pipeline_premium

    try:
        data = request.get_json()
        problem_text = data.get('problem_text', '')
        mode = data.get('mode', 'fast').lower()  # fast, accurate, premium

        if not problem_text:
            return jsonify({
                'success': False,
                'error': 'No problem text provided'
            }), 400

        # Use UnifiedPipeline if available, otherwise fall back to baseline
        if UNIFIED_PIPELINE_AVAILABLE and mode != 'legacy':
            # Map mode string to pipeline
            mode_map = {
                'fast': PipelineMode.FAST,
                'accurate': PipelineMode.ACCURATE,
                'premium': PipelineMode.PREMIUM
            }

            pipeline_mode = mode_map.get(mode, PipelineMode.FAST)

            # Select pipeline (with lazy initialization for ACCURATE/PREMIUM)
            if pipeline_mode == PipelineMode.FAST:
                pipeline = pipeline_fast
            elif pipeline_mode == PipelineMode.ACCURATE:
                if pipeline_accurate is None:
                    # Lazy init ACCURATE mode
                    try:
                        llm_config = LLMConfig(provider=LLMProvider.OLLAMA, model_name="mistral:7b")
                        pipeline_accurate = UnifiedPipeline(
                            mode=PipelineMode.ACCURATE,
                            output_dir="output/web_generated",
                            llm_config=llm_config
                        )
                        print("✅ UnifiedPipeline ACCURATE mode initialized")
                    except Exception as e:
                        return jsonify({
                            'success': False,
                            'error': f'ACCURATE mode requires Ollama: {str(e)}',
                            'hint': 'Install Ollama and run: ollama pull mistral:7b'
                        }), 503
                pipeline = pipeline_accurate
            else:  # PREMIUM
                if pipeline_premium is None:
                    # Lazy init PREMIUM mode
                    try:
                        llm_config = LLMConfig(provider=LLMProvider.OLLAMA, model_name="mistral:7b")
                        pipeline_premium = UnifiedPipeline(
                            mode=PipelineMode.PREMIUM,
                            output_dir="output/web_generated",
                            llm_config=llm_config
                        )
                        print("✅ UnifiedPipeline PREMIUM mode initialized")
                    except Exception as e:
                        return jsonify({
                            'success': False,
                            'error': f'PREMIUM mode requires Ollama + VLM: {str(e)}',
                            'hint': 'Install Ollama, transformers, and BLIP-2'
                        }), 503
                pipeline = pipeline_premium

            # Generate with UnifiedPipeline
            result = pipeline.generate(problem_text, save_files=False)

            # Convert PipelineResult to dict for JSON response
            result_dict = result.to_dict()

            # Add mode info to metadata
            if result_dict.get('metadata'):
                result_dict['metadata']['pipeline_mode'] = mode

            return jsonify(result_dict)

        else:
            # Fall back to baseline generator
            result = generator.generate(problem_text, save_files=False)

            if result['success']:
                # Add mode info
                result['metadata']['pipeline_mode'] = 'legacy'
                return jsonify({
                    'success': True,
                    'svg': result['svg'],
                    'scene_json': result['scene_json'],
                    'nlp_results': result['nlp_results'],
                    'metadata': result['metadata']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/batch', methods=['POST'])
def api_batch():
    """API endpoint for batch processing"""
    try:
        data = request.get_json()
        problems = data.get('problems', [])

        if not problems:
            return jsonify({
                'success': False,
                'error': 'No problems provided'
            }), 400

        # Process batch
        batch_problems = [(p['text'], p.get('filename', f'problem_{i}'))
                         for i, p in enumerate(problems)]

        result = generator.generate_batch(batch_problems, output_subdir='api_batch')

        return jsonify({
            'success': True,
            'batch_result': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'STEM Diagram Generator',
        'version': '2.0.0',
        'unified_pipeline_available': UNIFIED_PIPELINE_AVAILABLE,
        'enhanced_pipeline_available': ENHANCED_AVAILABLE,
        'modes': {
            'fast': pipeline_fast is not None,
            'accurate': pipeline_accurate is not None,
            'premium': pipeline_premium is not None
        }
    })


# ========================================
# Interactive Editor Routes
# ========================================

@app.route('/editor')
def editor():
    """Serve the interactive diagram editor"""
    if not ENHANCED_AVAILABLE:
        return "Enhanced Pipeline not available. Please install required dependencies.", 503
    return render_template('editor.html')


@app.route('/api/editor/generate', methods=['POST'])
def editor_generate():
    """Generate diagram from text for editor"""
    if not ENHANCED_AVAILABLE:
        return jsonify({'success': False, 'error': 'Enhanced Pipeline not available'}), 503

    try:
        data = request.json
        problem_text = data.get('problem', '')
        style = data.get('style', 'modern')
        enable_layout = data.get('enable_layout_optimization', True)
        enable_validation = data.get('enable_validation', True)
        enable_force_directed = data.get('enable_force_directed', False)

        if not problem_text:
            return jsonify({'success': False, 'error': 'No problem text provided'}), 400

        # Step 1: NLP extraction
        nlp_result = nlp_pipeline.extract_entities_and_relationships(problem_text)

        # Step 2: Build scene
        scene = scene_builder.build_scene(
            nlp_result,
            scene_id="editor_generated",
            title="Editor Generated Diagram"
        )

        # Step 3: Layout optimization
        if enable_layout:
            scene = layout_engine.optimize_layout(
                scene,
                enable_collision_avoidance=True,
                enable_force_directed=enable_force_directed
            )

        # Step 4: Validation and refinement
        quality = None
        if enable_validation:
            scene = refiner.refine(scene, max_iterations=3)
            quality = validator.validate(scene)

        # Step 5: Render to SVG
        component_library.set_style(style)
        renderer = EnhancedSVGRenderer(component_library)
        svg_content = renderer.render(scene)

        return jsonify({
            'success': True,
            'svg': svg_content,
            'scene': scene.to_dict(),
            'nlp_result': nlp_result,
            'quality_score': quality.overall_score if quality else None
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/editor/render', methods=['POST'])
def editor_render():
    """Render a scene to SVG"""
    if not ENHANCED_AVAILABLE:
        return jsonify({'success': False, 'error': 'Enhanced Pipeline not available'}), 503

    try:
        data = request.json
        scene_dict = data.get('scene', {})
        style = data.get('style', 'modern')

        # Reconstruct scene from JSON
        scene = UniversalScene.from_dict(scene_dict)

        # Render to SVG
        component_library.set_style(style)
        renderer = EnhancedSVGRenderer(component_library)
        svg_content = renderer.render(scene)

        return jsonify({
            'success': True,
            'svg': svg_content
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/editor/validate', methods=['POST'])
def editor_validate():
    """Validate a scene and return quality score"""
    if not ENHANCED_AVAILABLE:
        return jsonify({'success': False, 'error': 'Enhanced Pipeline not available'}), 503

    try:
        data = request.json
        scene_dict = data.get('scene', {})

        # Reconstruct scene from JSON
        scene = UniversalScene.from_dict(scene_dict)

        # Validate
        quality = validator.validate(scene)

        return jsonify({
            'success': True,
            'quality_score': quality.overall_score,
            'layout_score': quality.layout_score,
            'connectivity_score': quality.connectivity_score,
            'style_score': quality.style_score,
            'physics_score': quality.physics_score,
            'issues': [
                {
                    'category': issue.category,
                    'severity': issue.severity,
                    'message': issue.message,
                    'auto_fixable': issue.auto_fixable
                }
                for issue in quality.issues
            ]
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/editor/refine', methods=['POST'])
def editor_refine():
    """Automatically refine a scene to improve quality"""
    if not ENHANCED_AVAILABLE:
        return jsonify({'success': False, 'error': 'Enhanced Pipeline not available'}), 503

    try:
        data = request.json
        scene_dict = data.get('scene', {})
        max_iterations = data.get('max_iterations', 3)

        # Reconstruct scene from JSON
        scene = UniversalScene.from_dict(scene_dict)

        # Refine
        refined_scene = refiner.refine(scene, max_iterations=max_iterations)
        quality = validator.validate(refined_scene)

        return jsonify({
            'success': True,
            'scene': refined_scene.to_dict(),
            'quality_score': quality.overall_score
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/editor/optimize_layout', methods=['POST'])
def editor_optimize_layout():
    """Optimize scene layout"""
    if not ENHANCED_AVAILABLE:
        return jsonify({'success': False, 'error': 'Enhanced Pipeline not available'}), 503

    try:
        data = request.json
        scene_dict = data.get('scene', {})
        enable_force_directed = data.get('enable_force_directed', True)

        # Reconstruct scene from JSON
        scene = UniversalScene.from_dict(scene_dict)

        # Optimize layout
        optimized_scene = layout_engine.optimize_layout(
            scene,
            enable_collision_avoidance=True,
            enable_force_directed=enable_force_directed
        )

        return jsonify({
            'success': True,
            'scene': optimized_scene.to_dict()
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/editor/save', methods=['POST'])
def editor_save():
    """Save scene to file"""
    try:
        data = request.json
        scene_dict = data.get('scene', {})
        filename = data.get('filename', 'diagram')

        # Create output directory
        output_dir = Path('output/web_editor')
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save scene JSON
        filepath = output_dir / f"{filename}.json"
        with open(filepath, 'w') as f:
            json.dump(scene_dict, f, indent=2)

        return jsonify({
            'success': True,
            'filepath': str(filepath)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/editor/load', methods=['GET'])
def editor_load():
    """Load scene from file"""
    try:
        filename = request.args.get('filename', '')
        if not filename:
            return jsonify({'success': False, 'error': 'No filename provided'}), 400

        filepath = Path('output/web_editor') / f"{filename}.json"
        if not filepath.exists():
            return jsonify({'success': False, 'error': 'File not found'}), 404

        with open(filepath, 'r') as f:
            scene_dict = json.load(f)

        return jsonify({
            'success': True,
            'scene': scene_dict
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/editor/export', methods=['POST'])
def editor_export():
    """Export diagram to SVG file"""
    if not ENHANCED_AVAILABLE:
        return jsonify({'success': False, 'error': 'Enhanced Pipeline not available'}), 503

    try:
        data = request.json
        scene_dict = data.get('scene', {})
        filename = data.get('filename', 'diagram')
        style = data.get('style', 'modern')

        # Reconstruct scene from JSON
        scene = UniversalScene.from_dict(scene_dict)

        # Render to SVG
        component_library.set_style(style)
        renderer = EnhancedSVGRenderer(component_library)
        svg_content = renderer.render(scene)

        # Create output directory
        output_dir = Path('output/web_editor')
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save SVG
        filepath = output_dir / f"{filename}.svg"
        with open(filepath, 'w') as f:
            f.write(svg_content)

        return jsonify({
            'success': True,
            'filepath': str(filepath)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 70)
    print("STEM DIAGRAM GENERATOR - WEB INTERFACE v2.0")
    print("=" * 70)
    print("\n🌐 Starting web server...")
    print("📍 Main interface: http://localhost:5000")
    print("🏥 Health check: http://localhost:5000/health")
    print()

    # Show pipeline status
    if UNIFIED_PIPELINE_AVAILABLE:
        print("✅ UnifiedPipeline enabled - THREE MODES available:")
        print("   ⚡ FAST mode: Ready (keyword-based, offline)")
        print("   🧠 ACCURATE mode: Available (needs Ollama)")
        print("   💎 PREMIUM mode: Available (needs Ollama + VLM)")
    else:
        print("⚠️  UnifiedPipeline not available - using legacy generator")

    print()
    if ENHANCED_AVAILABLE:
        print("🎨 Interactive Editor: http://localhost:5000/editor")
    else:
        print("⚠️  Interactive Editor unavailable (Enhanced Pipeline not loaded)")

    print("\n⚡ Press Ctrl+C to stop\n")
    print("=" * 70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
