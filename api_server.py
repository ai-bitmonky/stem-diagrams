"""
Flask API Server for Diagram Generation
Wraps unified_diagram_pipeline.py for web UI access
With DeepSeek AI LLM Features
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

# Initialize pipeline once at startup
print("Initializing UnifiedDiagramPipeline...")
api_key = os.environ.get('DEEPSEEK_API_KEY')

if api_key:
    print(f"✅ DeepSeek API key found (starts with {api_key[:7]}...)")
else:
    print("⚠️  DeepSeek API key not found - LLM features will be disabled")
    print("   Set: export DEEPSEEK_API_KEY='your-key'")

config = PipelineConfig(
    api_key=api_key,
    api_base_url="https://api.deepseek.com",  # DeepSeek endpoint
    api_model="deepseek-chat",
    validation_mode="standard",

    # Core features
    enable_layout_optimization=True,
    enable_domain_embellishments=True,
    enable_ai_validation=False,  # Disable for speed

    # Advanced features
    enable_property_graph=True,
    enable_nlp_enrichment=True,
    enable_complexity_assessment=True,
    enable_strategic_planning=True,
    enable_ontology_validation=True,
    enable_z3_optimization=False,

    # NLP tools - Enable available tools (install others with pip install stanza scibert, etc.)
    # Full list: ['openie', 'stanza', 'dygie', 'scibert', 'chemdataextractor', 'mathbert', 'amr']
    nlp_tools=['openie'],  # Start with OpenIE (always available)

    # LLM Planning with DeepSeek (Auto-enabled if API key present)
    enable_llm_planning=bool(api_key),
    llm_planner_api_model="deepseek-chat",

    # LLM Auditing with DeepSeek (Auto-enabled if API key present)
    enable_llm_auditing=bool(api_key),
    auditor_backend='deepseek' if api_key else 'mock',  # Use DeepSeek backend
    auditor_api_key=api_key,

    # NEW: DeepSeek 3 API Calls (Roadmap Implementation)
    enable_deepseek_enrichment=bool(api_key),  # Call #1: Entity enrichment
    enable_deepseek_audit=bool(api_key),        # Call #2: Plan auditing
    enable_deepseek_validation=bool(api_key),   # Call #3: Semantic validation
    deepseek_api_key=api_key,
    deepseek_model="deepseek-chat",
    deepseek_base_url="https://api.deepseek.com",
)

try:
    pipeline = UnifiedDiagramPipeline(config)

    # Configure DeepSeek for LLM Planner
    if api_key and pipeline.llm_planner:
        try:
            from openai import OpenAI
            pipeline.llm_planner.api_client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com",
                timeout=180
            )
            print("✅ LLM Planner configured with DeepSeek")
        except ImportError as e:
            if 'socksio' in str(e) or 'socks' in str(e).lower():
                print("⚠️  LLM Planner: Proxy configuration issue, using default config")
                print("   (LLM Planning is still active with API key)")
            else:
                raise

    # Configure DeepSeek for Auditor
    if api_key and pipeline.auditor:
        try:
            from openai import OpenAI as AuditorOpenAI
            if hasattr(pipeline.auditor, 'llm_client'):
                pipeline.auditor.llm_client = AuditorOpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com",
                    timeout=180
                )
                print("✅ LLM Auditor configured with DeepSeek")
        except ImportError as e:
            if 'socksio' in str(e) or 'socks' in str(e).lower():
                print("⚠️  LLM Auditor: Proxy configuration issue, using default config")
                print("   (LLM Auditing is still active)")
            else:
                raise

    print("✅ Pipeline initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize pipeline: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


@app.route('/api/generate', methods=['POST'])
def generate_diagram():
    """Generate diagram from problem text"""
    try:
        # Get problem text from request
        data = request.get_json()
        problem_text = data.get('problem_text', '')

        if not problem_text:
            return jsonify({'error': 'problem_text is required'}), 400

        print(f"\n{'='*80}")
        print(f"Generating diagram for problem:")
        print(f"{problem_text[:100]}...")
        print(f"{'='*80}\n")

        # Generate diagram
        result = pipeline.generate(problem_text)

        # Extract SVG content
        svg_content = result.svg

        # Build metadata
        metadata = {
            'complexity_score': result.complexity_score or 0.0,
            'selected_strategy': result.selected_strategy or 'unknown',
            'property_graph_nodes': len(result.property_graph.get_all_nodes()) if result.property_graph else 0,
            'property_graph_edges': len(result.property_graph.get_edges()) if result.property_graph else 0,
            'ontology_validation': result.ontology_validation,
            'nlp_tools_used': list(result.nlp_results.keys()) if result.nlp_results else []
        }

        print(f"\n✅ Diagram generated successfully")
        print(f"   Complexity: {metadata['complexity_score']:.2f}")
        print(f"   Strategy: {metadata['selected_strategy']}")
        print(f"   Property Graph: {metadata['property_graph_nodes']} nodes, {metadata['property_graph_edges']} edges")
        print()

        return jsonify({
            'svg': svg_content,
            'metadata': metadata
        })

    except Exception as e:
        print(f"\n❌ Error generating diagram: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'pipeline': 'unified_diagram_pipeline.py',
        'features': {
            'property_graph': config.enable_property_graph,
            'nlp_enrichment': config.enable_nlp_enrichment,
            'complexity_assessment': config.enable_complexity_assessment,
            'strategic_planning': config.enable_strategic_planning,
            'ontology_validation': config.enable_ontology_validation
        }
    })


if __name__ == '__main__':
    print("\n" + "="*80)
    print("STEM Diagram Generator API Server")
    print("="*80)
    print("\nEndpoints:")
    print("  POST /api/generate - Generate diagram from problem text")
    print("  GET  /api/health   - Health check")
    print("\nServer starting on http://localhost:5001")
    print("="*80 + "\n")

    app.run(host='127.0.0.1', port=5001, debug=False)
