# DeepSeek AI Setup Guide

**Date:** November 10, 2025
**Status:** ✅ **Ready to Use**

---

## Why DeepSeek?

DeepSeek AI offers excellent value for LLM-powered features:

| Feature | DeepSeek | OpenAI GPT-4 | Claude Opus |
|---------|----------|--------------|-------------|
| **Input Cost** | $0.14 / 1M tokens | $30.00 / 1M tokens | $15.00 / 1M tokens |
| **Output Cost** | $0.28 / 1M tokens | $60.00 / 1M tokens | $75.00 / 1M tokens |
| **Per Diagram** | ~$0.001-0.01 | ~$0.10-0.50 | ~$0.15-0.75 |
| **API Compatible** | OpenAI-compatible | OpenAI | Anthropic |
| **Quality** | Excellent for reasoning | Best overall | Best for analysis |

**Cost Example:**
- 100 diagrams with DeepSeek: ~$0.50-1.00
- 100 diagrams with GPT-4: ~$10-50
- 100 diagrams with Claude: ~$15-75

**DeepSeek is 50-100x cheaper!**

---

## Quick Start

### Step 1: Get DeepSeek API Key

1. Go to https://platform.deepseek.com/
2. Sign up for an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

### Step 2: Set Environment Variable

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export DEEPSEEK_API_KEY="sk-your-api-key-here"

# Or set for current session
export DEEPSEEK_API_KEY="sk-your-api-key-here"

# Verify it's set
echo $DEEPSEEK_API_KEY
```

### Step 3: Enable in api_server.py

**Option A: Enable LLM Planning Only (Cheapest)**
```python
# api_server.py - around line 25
config = PipelineConfig(
    # DeepSeek API config (already set by default!)
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    api_base_url="https://api.deepseek.com",  # Already default
    api_model="deepseek-chat",  # Already default

    # Enable LLM planning
    enable_llm_planning=True,
    llm_planner_api_model="deepseek-chat",  # Use DeepSeek for planning

    # Keep auditing on mock
    enable_llm_auditing=False,  # Or use mock
    auditor_backend='mock',
)
```

**Option B: Enable LLM Auditing Only**
```python
config = PipelineConfig(
    # DeepSeek API
    api_key=os.getenv('DEEPSEEK_API_KEY'),

    # No LLM planning
    enable_llm_planning=False,

    # Enable auditing with DeepSeek
    enable_llm_auditing=True,
    auditor_backend='gpt',  # DeepSeek is OpenAI-compatible
    auditor_api_key=os.getenv('DEEPSEEK_API_KEY'),
)
```

**Option C: Enable Both (Recommended)**
```python
config = PipelineConfig(
    # DeepSeek API
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    api_base_url="https://api.deepseek.com",
    api_model="deepseek-chat",

    # LLM Planning with DeepSeek
    enable_llm_planning=True,
    llm_planner_api_model="deepseek-chat",

    # LLM Auditing with DeepSeek
    enable_llm_auditing=True,
    auditor_backend='gpt',  # DeepSeek is OpenAI-compatible
    auditor_api_key=os.getenv('DEEPSEEK_API_KEY'),
)
```

### Step 4: Update LLM Planner for DeepSeek

Since DeepSeek is OpenAI-compatible, we need to configure the planner to use DeepSeek's base URL:

```python
# api_server.py - after imports, add:
import os
from openai import OpenAI

# Then in config:
config = PipelineConfig(
    # ... other config ...

    enable_llm_planning=True,
    llm_planner_api_model="deepseek-chat",
)

# Initialize pipeline
pipeline = UnifiedDiagramPipeline(config)

# Configure DeepSeek client for LLM planner
if pipeline.llm_planner and pipeline.llm_planner.api_client:
    pipeline.llm_planner.api_client = OpenAI(
        api_key=os.getenv('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com",
        timeout=180
    )
```

### Step 5: Restart Flask

```bash
python3 api_server.py
```

You should see:
```
✓ Phase 1+2: LLM Diagram Planner [ACTIVE]
✓ Phase 7: LLM Auditor [ACTIVE]
```

---

## Complete Example Configuration

Here's a complete [api_server.py](api_server.py) configuration with DeepSeek:

```python
#!/usr/bin/env python3
"""
Flask API Server with DeepSeek LLM Features
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

# Get DeepSeek API key
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

if not DEEPSEEK_API_KEY:
    print("⚠️  WARNING: DEEPSEEK_API_KEY not set")
    print("   LLM features will be disabled")
    print("   Set: export DEEPSEEK_API_KEY='your-key'")

# Configure pipeline with DeepSeek
config = PipelineConfig(
    # DeepSeek API configuration
    api_key=DEEPSEEK_API_KEY,
    api_base_url="https://api.deepseek.com",
    api_model="deepseek-chat",
    api_timeout=180,

    # Enable advanced features
    enable_property_graph=True,
    enable_nlp_enrichment=True,
    enable_complexity_assessment=True,
    enable_strategic_planning=True,
    enable_ontology_validation=True,

    # NLP tools - All 7 active
    nlp_tools=['openie', 'stanza', 'dygie', 'scibert',
               'chemdataextractor', 'mathbert', 'amr'],

    # LLM Planning with DeepSeek (ENABLED)
    enable_llm_planning=True if DEEPSEEK_API_KEY else False,
    llm_planner_api_model="deepseek-chat",

    # LLM Auditing with DeepSeek (ENABLED)
    enable_llm_auditing=True if DEEPSEEK_API_KEY else False,
    auditor_backend='gpt' if DEEPSEEK_API_KEY else 'mock',
    auditor_api_key=DEEPSEEK_API_KEY,
)

# Initialize pipeline
try:
    pipeline = UnifiedDiagramPipeline(config)

    # Configure DeepSeek client for LLM planner
    if DEEPSEEK_API_KEY and pipeline.llm_planner:
        pipeline.llm_planner.api_client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com",
            timeout=180
        )
        print("✅ LLM Planner configured with DeepSeek")

    # Configure DeepSeek client for auditor
    if DEEPSEEK_API_KEY and pipeline.auditor:
        from openai import OpenAI as AuditorOpenAI
        if hasattr(pipeline.auditor, 'llm_client'):
            pipeline.auditor.llm_client = AuditorOpenAI(
                api_key=DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com",
                timeout=180
            )
            print("✅ LLM Auditor configured with DeepSeek")

    print("✅ Pipeline initialized successfully with DeepSeek")

except Exception as e:
    print(f"❌ Failed to initialize pipeline: {e}")
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
            'nlp_tools_used': list(result.nlp_results.keys()) if result.nlp_results else [],
            'llm_plan_generated': result.llm_plan is not None,
            'audit_score': result.audit_report.get('overall_score') if result.audit_report else None,
        }

        print(f"\n{'='*80}")
        print(f"✅ Diagram generated successfully!")
        if result.llm_plan:
            print(f"   🤖 LLM Plan: {len(result.llm_plan.get('entities', []))} entities")
        if result.audit_report:
            print(f"   🔍 Audit Score: {result.audit_report.get('overall_score', 0):.1f}/10")
        print(f"{'='*80}\n")

        return jsonify({
            'svg': svg_content,
            'metadata': metadata
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'pipeline': 'ready',
        'deepseek_configured': DEEPSEEK_API_KEY is not None,
        'llm_planning_active': config.enable_llm_planning,
        'llm_auditing_active': config.enable_llm_auditing,
        'nlp_tools': len(config.nlp_tools)
    })


if __name__ == '__main__':
    print("="*80)
    print("STEM Diagram Generator API Server with DeepSeek AI")
    print("="*80)
    print("\nConfiguration:")
    print(f"  DeepSeek API: {'✅ Configured' if DEEPSEEK_API_KEY else '❌ Not configured'}")
    print(f"  LLM Planning: {'✅ Enabled' if config.enable_llm_planning else '❌ Disabled'}")
    print(f"  LLM Auditing: {'✅ Enabled' if config.enable_llm_auditing else '❌ Disabled'}")
    print(f"  NLP Tools: {len(config.nlp_tools)} active")
    print("\nEndpoints:")
    print("  POST /api/generate - Generate diagram from problem text")
    print("  GET  /api/health   - Health check")
    print("\nServer starting on http://localhost:5001")
    print("="*80 + "\n")

    app.run(host='127.0.0.1', port=5001, debug=True)
```

---

## Testing DeepSeek

### Test 1: Verify API Key

```bash
# Test DeepSeek API directly
python3 core/deepseek_llm_adapter.py
```

Expected output:
```
============================================================
DeepSeek LLM Adapter Test
============================================================
✅ DeepSeek client initialized
✅ Chat completion successful:
   Response: Newton's first law states that...
   Tokens: 45
   Cost: $0.000008

✅ JSON mode successful:
   Response: {"concepts": ["mechanics", "thermodynamics", "electromagnetism"]}

============================================================
✅ All tests passed!
============================================================
```

### Test 2: Test with Pipeline

```python
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig
import os

config = PipelineConfig(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    enable_llm_planning=True,
    llm_planner_api_model="deepseek-chat"
)

pipeline = UnifiedDiagramPipeline(config)

# Configure DeepSeek
from openai import OpenAI
if pipeline.llm_planner:
    pipeline.llm_planner.api_client = OpenAI(
        api_key=os.getenv('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com"
    )

# Test
problem = "A 5 kg block slides down a 30 degree incline with friction coefficient 0.25"
result = pipeline.generate(problem)

print(f"✅ Generated diagram")
if result.llm_plan:
    print(f"   LLM Plan: {len(result.llm_plan['entities'])} entities")
    print(f"   Cost: ~$0.001")
```

### Test 3: Compare with Mock

Run the same diagram with mock vs DeepSeek and compare quality:

```bash
# With mock (free, basic)
python3 api_server.py  # With auditor_backend='mock'

# With DeepSeek (cheap, AI-powered)
python3 api_server.py  # With DeepSeek configured
```

---

## Cost Monitoring

Track your DeepSeek usage:

```python
# In api_server.py, add after diagram generation:

if result.metadata and 'trace' in result.metadata:
    # Estimate tokens (rough)
    problem_tokens = len(problem_text.split()) * 1.3  # ~1.3 tokens per word

    planning_cost = 0
    if result.llm_plan:
        planning_tokens = 500  # Typical plan
        planning_cost = (problem_tokens + planning_tokens) / 1_000_000 * 0.28

    auditing_cost = 0
    if result.audit_report:
        audit_tokens = 1000  # Typical audit
        auditing_cost = (problem_tokens + audit_tokens) / 1_000_000 * 0.28

    total_cost = planning_cost + auditing_cost

    print(f"   💰 Estimated cost: ${total_cost:.6f}")
```

---

## Troubleshooting

### Issue 1: "API key not set"

**Solution:**
```bash
# Check if key is set
echo $DEEPSEEK_API_KEY

# If empty, set it
export DEEPSEEK_API_KEY="sk-your-key"

# Add to shell profile to persist
echo 'export DEEPSEEK_API_KEY="sk-your-key"' >> ~/.bashrc
source ~/.bashrc
```

### Issue 2: "Connection error"

**Symptom:**
```
ConnectionError: Unable to connect to DeepSeek API
```

**Solutions:**
1. Check internet connection
2. Verify API key is valid
3. Check if DeepSeek API is accessible:
   ```bash
   curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
        https://api.deepseek.com/models
   ```

### Issue 3: "Model not found"

**Solution:** Use correct model name:
- ✅ `deepseek-chat` - General purpose
- ✅ `deepseek-coder` - Code-focused
- ❌ `gpt-4` - Wrong (OpenAI model)

### Issue 4: Rate limiting

**Symptom:**
```
RateLimitError: Rate limit exceeded
```

**Solutions:**
1. Add delays between requests
2. Upgrade DeepSeek plan
3. Use exponential backoff retry

---

## DeepSeek vs Other Options

| Criteria | DeepSeek | Ollama (Local) | OpenAI GPT-4 |
|----------|----------|----------------|--------------|
| **Cost** | 💰 $0.001/diagram | 💰💰💰 Free | 💰💰💰💰💰 $0.10/diagram |
| **Quality** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Speed** | ⚡⚡⚡ Fast | ⚡ Slow | ⚡⚡⚡⚡ Fast |
| **Setup** | 🔧 Easy (API key) | 🔧🔧🔧 Complex | 🔧 Easy (API key) |
| **Privacy** | ❌ Cloud | ✅ Local | ❌ Cloud |
| **Offline** | ❌ No | ✅ Yes | ❌ No |

**Recommendation:**
- **Development:** Use DeepSeek (cheap, easy)
- **Production (budget):** Use DeepSeek
- **Production (premium):** Use GPT-4
- **Privacy-sensitive:** Use Ollama (local)

---

## Next Steps

1. ✅ Get DeepSeek API key
2. ✅ Set DEEPSEEK_API_KEY environment variable
3. ✅ Update api_server.py with configuration above
4. ✅ Restart Flask server
5. ✅ Test with a diagram
6. ✅ Monitor costs in DeepSeek dashboard

---

**Cost Estimate for 1000 Diagrams:**
- DeepSeek: ~$1-10
- GPT-4: ~$100-500
- Claude: ~$150-750
- Ollama: $0 (but requires hardware)

**DeepSeek saves 99% compared to premium APIs!**

---

**Last Updated:** November 10, 2025
**Status:** ✅ Production Ready
**Documentation:** Complete
