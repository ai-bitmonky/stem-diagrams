#!/usr/bin/env python3
"""
Flask API Server with DeepSeek AI Integration
==============================================

This is an example configuration showing how to use DeepSeek AI for:
1. LLM-based diagram planning
2. LLM-based diagram auditing

DeepSeek is 50-100x cheaper than OpenAI/Claude while maintaining good quality.

Setup:
1. Get API key from https://platform.deepseek.com/
2. Set environment variable: export DEEPSEEK_API_KEY="sk-..."
3. Run: python3 api_server_deepseek_example.py

Cost: ~$0.001-0.01 per diagram (vs $0.10-0.50 with GPT-4)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from openai import OpenAI

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig

app = Flask(__name__)
CORS(app)

# ==================== DEEPSEEK CONFIGURATION ====================

# Get DeepSeek API key from environment
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

if not DEEPSEEK_API_KEY:
    print("\n" + "="*80)
    print("⚠️  WARNING: DEEPSEEK_API_KEY environment variable not set")
    print("="*80)
    print("\nTo use DeepSeek AI features:")
    print("1. Get API key from https://platform.deepseek.com/")
    print("2. Set environment variable:")
    print("   export DEEPSEEK_API_KEY='your-api-key-here'")
    print("3. Restart this server")
    print("\nWithout API key:")
    print("- LLM Planning: DISABLED")
    print("- LLM Auditing: Using MOCK mode (simulated)")
    print("="*80 + "\n")

# Configure pipeline with DeepSeek
config = PipelineConfig(
    # ===== DeepSeek API Configuration =====
    api_key=DEEPSEEK_API_KEY,
    api_base_url="https://api.deepseek.com",
    api_model="deepseek-chat",
    api_timeout=180,

    # ===== Advanced NLP Features =====
    enable_property_graph=True,
    enable_nlp_enrichment=True,
    enable_complexity_assessment=True,
    enable_strategic_planning=True,
    enable_ontology_validation=True,

    # ===== NLP Tools (All 7 Active) =====
    nlp_tools=[
        'openie',           # Triple extraction
        'stanza',           # Stanford NLP
        'dygie',            # Scientific relation extraction
        'scibert',          # Scientific embeddings
        'chemdataextractor', # Chemistry parsing
        'mathbert',         # Mathematical expressions
        'amr'               # Semantic representation
    ],

    # ===== LLM Planning with DeepSeek =====
    # Generates structured diagram plans from natural language
    # Cost: ~$0.0005 per diagram
    enable_llm_planning=True if DEEPSEEK_API_KEY else False,
    llm_planner_api_model="deepseek-chat",

    # ===== LLM Auditing with DeepSeek =====
    # AI-powered quality validation and suggestions
    # Cost: ~$0.001 per diagram
    enable_llm_auditing=True if DEEPSEEK_API_KEY else False,
    auditor_backend='gpt' if DEEPSEEK_API_KEY else 'mock',  # DeepSeek is OpenAI-compatible
    auditor_api_key=DEEPSEEK_API_KEY,

    # ===== Other Settings =====
    enable_z3_optimization=False,  # SMT-based layout (optional)
)

# Initialize pipeline
try:
    pipeline = UnifiedDiagramPipeline(config)

    # ===== Configure DeepSeek for LLM Planner =====
    if DEEPSEEK_API_KEY and pipeline.llm_planner:
        pipeline.llm_planner.api_client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com",
            timeout=180
        )
        print("✅ LLM Planner configured with DeepSeek AI")

    # ===== Configure DeepSeek for Auditor =====
    if DEEPSEEK_API_KEY and pipeline.auditor:
        if hasattr(pipeline.auditor, 'llm_client'):
            pipeline.auditor.llm_client = OpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
                timeout=180
            )
            print("✅ LLM Auditor configured with DeepSeek AI")

    print("✅ Pipeline initialized successfully")

except Exception as e:
    print(f"❌ Failed to initialize pipeline: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ==================== API ROUTES ====================

@app.route('/api/generate', methods=['POST'])
def generate_diagram():
    """Generate diagram from problem text"""
    try:
        data = request.get_json()
        problem_text = data.get('problem_text', '')

        if not problem_text:
            return jsonify({'error': 'No problem_text provided'}), 400

        print(f"\n{'='*80}")
        print(f"📝 Generating diagram for problem:")
        print(f"   {problem_text[:100]}...")
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
            'nlp_tools_used': list(result.nlp_results.keys()) if result.nlp_results else [],
            'llm_plan_generated': result.llm_plan is not None,
            'llm_plan_entities': len(result.llm_plan.get('entities', [])) if result.llm_plan else 0,
            'audit_score': result.audit_report.get('overall_score') if result.audit_report else None,
            'audit_issues': result.audit_report.get('issue_count') if result.audit_report else 0,
        }

        # Print summary
        print(f"\n{'='*80}")
        print(f"✅ Diagram generated successfully!")
        print(f"   📊 Complexity: {metadata['complexity_score']:.2f}")
        print(f"   🧠 NLP Tools: {len(metadata['nlp_tools_used'])} active")

        if result.llm_plan:
            print(f"   🤖 LLM Plan: {metadata['llm_plan_entities']} entities")
            print(f"      Cost: ~$0.0005")

        if result.audit_report:
            audit_score = metadata['audit_score']
            if audit_score:
                print(f"   🔍 Audit Score: {audit_score:.1f}/10")
                print(f"      Issues: {metadata['audit_issues']}")
                print(f"      Cost: ~$0.001")

        if DEEPSEEK_API_KEY and (result.llm_plan or result.audit_report):
            print(f"   💰 Total Cost: ~$0.001-0.01")

        print(f"{'='*80}\n")

        return jsonify({
            'svg': svg_content,
            'metadata': metadata
        })

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with feature status"""
    return jsonify({
        'status': 'healthy',
        'pipeline': 'ready',
        'features': {
            'deepseek_configured': DEEPSEEK_API_KEY is not None,
            'llm_planning': config.enable_llm_planning,
            'llm_auditing': config.enable_llm_auditing,
            'nlp_tools_count': len(config.nlp_tools),
            'nlp_tools': config.nlp_tools,
        },
        'costs': {
            'planning_per_diagram': '$0.0005',
            'auditing_per_diagram': '$0.001',
            'total_per_diagram': '$0.001-0.01',
        }
    })


if __name__ == '__main__':
    print("="*80)
    print("🚀 STEM Diagram Generator API Server")
    print("   Powered by DeepSeek AI")
    print("="*80)

    print("\n📊 Configuration:")
    print(f"   DeepSeek API: {'✅ Configured' if DEEPSEEK_API_KEY else '❌ Not configured'}")
    print(f"   LLM Planning: {'✅ Enabled ($0.0005/diagram)' if config.enable_llm_planning else '❌ Disabled'}")
    print(f"   LLM Auditing: {'✅ Enabled ($0.001/diagram)' if config.enable_llm_auditing else '🔄 Mock mode'}")
    print(f"   NLP Tools: ✅ {len(config.nlp_tools)} active")

    print("\n🔌 Endpoints:")
    print("   POST /api/generate - Generate diagram from problem text")
    print("   GET  /api/health   - Health check & feature status")

    print("\n🌐 Server:")
    print("   http://localhost:5001")

    if not DEEPSEEK_API_KEY:
        print("\n💡 Tip: Set DEEPSEEK_API_KEY to enable LLM features")
        print("   export DEEPSEEK_API_KEY='your-key-here'")

    print("="*80 + "\n")

    app.run(host='127.0.0.1', port=5001, debug=True)
