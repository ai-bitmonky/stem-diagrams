# LLM Features Implementation Guide

**Date:** November 10, 2025
**Status:** ✅ **FULLY IMPLEMENTED & INTEGRATED**

---

## Executive Summary

The STEM Diagram Generator now has **complete LLM integration** for both planning and validation:

1. **✅ LLM-based Planning** - Generate diagram plans from natural language
2. **✅ LLM-based Auditing** - Validate diagram quality with AI feedback

Both features are **implemented and integrated** into the unified pipeline, but **disabled by default** to avoid requiring LLM setup.

---

## Table of Contents

1. [Feature Overview](#feature-overview)
2. [LLM Planning](#llm-planning)
3. [LLM Auditing](#llm-auditing)
4. [How to Enable](#how-to-enable)
5. [LLM Backend Options](#llm-backend-options)
6. [Setup Guides](#setup-guides)
7. [Configuration Reference](#configuration-reference)
8. [Troubleshooting](#troubleshooting)

---

## Feature Overview

### 1. LLM Planning (Phase 1-2)

**Purpose:** Use LLMs to generate structured diagram plans from natural language descriptions.

**Location:** [core/llm_planner.py](core/llm_planner.py)

**Integration:** [unified_diagram_pipeline.py:402-413, 656-670](unified_diagram_pipeline.py)

**How it works:**
```
Problem Text
    ↓
LLM Planning (Ollama/GPT)
    ↓
Structured Plan (entities, relationships, constraints)
    ↓
Scene Building
```

**Benefits:**
- Natural language understanding
- Better entity recognition
- Relationship inference
- Layout hints from semantic understanding

---

### 2. LLM Auditing (Phase 7)

**Purpose:** Use LLMs to validate diagram quality and suggest improvements.

**Location:** [core/auditor/diagram_auditor.py](core/auditor/diagram_auditor.py)

**Integration:** [unified_diagram_pipeline.py:424-438, 789-815](unified_diagram_pipeline.py)

**How it works:**
```
Generated Diagram (SVG + Specs)
    ↓
LLM Auditing (Claude/GPT)
    ↓
Quality Score + Issues + Suggestions
    ↓
Optional Refinement
```

**Benefits:**
- Scientific accuracy validation
- Visual clarity assessment
- Labeling improvements
- Layout suggestions

---

## LLM Planning

### Features

**Draft Plan Generation:**
- Entities: Physical objects, components, forces
- Relationships: Connections, interactions, dependencies
- Constraints: Spatial, physical, geometric rules

**Multi-Backend Support:**
- Local LLM (Ollama): Mistral, Llama2, etc.
- API LLM (OpenAI): GPT-4, GPT-3.5-turbo
- Verification: Optional API-based plan verification

**Plan Structure:**
```python
DiagramPlan(
    domain='physics',
    diagram_type='force_diagram',
    entities=[
        DiagramPlanEntity(
            id='block',
            type='rigid_body',
            label='Block (m=5kg)',
            properties={'mass': 5.0, 'unit': 'kg'}
        ),
        # ... more entities
    ],
    relationships=[
        DiagramPlanRelationship(
            source_id='force_gravity',
            target_id='block',
            type='applies_to',
            properties={}
        )
    ],
    constraints=[
        DiagramPlanConstraint(
            type='spatial',
            description='Block rests on surface',
            entities=['block', 'surface'],
            parameters={'alignment': 'bottom'}
        )
    ]
)
```

### When to Use

**Best for:**
- Complex multi-entity problems
- Problems with implicit relationships
- Natural language heavy descriptions
- Problems requiring semantic understanding

**Not needed for:**
- Simple single-object problems
- Well-structured canonical specs
- Problems where rule-based planning works well

---

## LLM Auditing

### Features

**Quality Scoring:** 0-10 overall score

**Issue Detection:**
- **Critical:** Scientifically incorrect
- **Major:** Misleading or confusing
- **Minor:** Stylistic improvements
- **Suggestion:** Optional enhancements

**Issue Categories:**
- Scientific Accuracy
- Visual Clarity
- Labeling
- Layout
- Completeness
- Consistency

**Example Audit Result:**
```json
{
  "overall_score": 7.5,
  "issues": [
    {
      "category": "scientific_accuracy",
      "severity": "major",
      "description": "Force vector direction appears incorrect",
      "location": "Object 'block', force 'F_friction'",
      "suggestion": "Friction force should oppose motion direction",
      "confidence": 0.9
    }
  ],
  "suggestions": [
    "Add magnitude labels to all force vectors",
    "Use consistent arrow styles",
    "Include coordinate system reference"
  ]
}
```

### Supported Backends

1. **Claude (Anthropic):**
   - Models: claude-3-opus, claude-3-sonnet, claude-3-haiku
   - Best for: Detailed scientific validation
   - Requires: `ANTHROPIC_API_KEY` environment variable

2. **GPT (OpenAI):**
   - Models: gpt-4, gpt-4-turbo, gpt-3.5-turbo
   - Best for: General quality assessment
   - Requires: `OPENAI_API_KEY` environment variable

3. **Local Models:**
   - Via transformers library
   - Best for: Offline/privacy-sensitive use
   - Requires: Local model setup

4. **Mock:**
   - Simulated responses for testing
   - No setup required
   - **Currently active by default**

---

## How to Enable

### Option 1: Enable LLM Planning Only

```python
# In api_server.py or your script
config = PipelineConfig(
    # ... other config ...

    # Enable LLM planning
    enable_llm_planning=True,
    llm_planner_local_model="mistral:7b",  # Ollama model
    llm_planner_ollama_url="http://localhost:11434",

    # Optional: API model for verification
    # llm_planner_api_model="gpt-4",  # Requires OPENAI_API_KEY
)
```

**Prerequisites:**
- Ollama installed and running
- Model downloaded: `ollama pull mistral:7b`

---

### Option 2: Enable LLM Auditing Only

```python
# In api_server.py
config = PipelineConfig(
    # ... other config ...

    # Enable LLM auditing
    enable_llm_auditing=True,
    auditor_backend='claude',  # or 'gpt', 'local', 'mock'
    auditor_api_key=os.getenv('ANTHROPIC_API_KEY'),
)
```

**Prerequisites:**
- API key set in environment
- For Claude: `export ANTHROPIC_API_KEY=sk-ant-...`
- For GPT: `export OPENAI_API_KEY=sk-...`

---

### Option 3: Enable Both

```python
config = PipelineConfig(
    # ... other config ...

    # LLM Planning
    enable_llm_planning=True,
    llm_planner_local_model="mistral:7b",

    # LLM Auditing
    enable_llm_auditing=True,
    auditor_backend='claude',
    auditor_api_key=os.getenv('ANTHROPIC_API_KEY'),
)
```

---

## LLM Backend Options

### Local LLMs (Ollama)

**Advantages:**
- Free, unlimited usage
- Privacy (runs locally)
- Fast (once model loaded)
- No internet required

**Disadvantages:**
- Requires setup
- Requires disk space (~4-7GB per model)
- Requires decent hardware (8GB+ RAM recommended)

**Recommended Models:**
- **mistral:7b** - Good balance of quality and speed
- **llama2:7b** - Alternative, slightly slower
- **codellama:7b** - Better for technical understanding

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download model
ollama pull mistral:7b

# Start Ollama server (if not auto-started)
ollama serve
```

---

### API LLMs (OpenAI/Anthropic)

**Advantages:**
- No local setup required
- State-of-the-art quality
- Always latest models

**Disadvantages:**
- Costs money (pay per token)
- Requires internet
- Privacy considerations

**Cost Estimates:**
- GPT-3.5-turbo: ~$0.01 per diagram
- GPT-4: ~$0.10 per diagram
- Claude Sonnet: ~$0.05 per diagram
- Claude Opus: ~$0.15 per diagram

**Setup:**
```bash
# For OpenAI
export OPENAI_API_KEY="sk-..."

# For Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Add to ~/.bashrc or ~/.zshrc to persist
```

---

## Setup Guides

### Complete Setup: Ollama + Claude

This setup gives you:
- Local planning (free, fast)
- Cloud auditing (high quality)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull model
ollama pull mistral:7b

# 3. Get Claude API key from https://console.anthropic.com/
export ANTHROPIC_API_KEY="sk-ant-..."

# 4. Update api_server.py
```

```python
# api_server.py
config = PipelineConfig(
    # Enable both features
    enable_llm_planning=True,
    llm_planner_local_model="mistral:7b",

    enable_llm_auditing=True,
    auditor_backend='claude',
    auditor_api_key=os.getenv('ANTHROPIC_API_KEY'),
)
```

```bash
# 5. Restart Flask
python3 api_server.py
```

---

### Budget Setup: Ollama Only

This setup is completely free but planning-only (no auditing):

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull model
ollama pull mistral:7b

# 3. Update api_server.py
```

```python
config = PipelineConfig(
    enable_llm_planning=True,
    llm_planner_local_model="mistral:7b",

    # Keep auditing on mock
    enable_llm_auditing=True,
    auditor_backend='mock',
)
```

---

### Premium Setup: GPT-4 for Both

This setup uses GPT-4 for both planning and auditing:

```bash
# 1. Get API key from https://platform.openai.com/
export OPENAI_API_KEY="sk-..."

# 2. Update api_server.py
```

```python
config = PipelineConfig(
    enable_llm_planning=True,
    llm_planner_local_model=None,  # Disable local
    llm_planner_api_model="gpt-4",

    enable_llm_auditing=True,
    auditor_backend='gpt',
    auditor_api_key=os.getenv('OPENAI_API_KEY'),
)
```

---

## Configuration Reference

### Planning Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_llm_planning` | bool | False | Enable LLM-based planning |
| `llm_planner_local_model` | str | "mistral:7b" | Ollama model name |
| `llm_planner_api_model` | str\|None | None | OpenAI model for planning/verification |
| `llm_planner_ollama_url` | str | "http://localhost:11434" | Ollama API endpoint |

### Auditing Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_llm_auditing` | bool | True | Enable LLM-based auditing |
| `auditor_backend` | str | "mock" | Backend: 'claude', 'gpt', 'local', 'mock' |
| `auditor_api_key` | str\|None | None | API key for Claude/GPT |

---

## Troubleshooting

### Issue 1: "Connection refused" for Ollama

**Symptom:**
```
ConnectionError: ('Connection aborted.', ConnectionRefusedError(61, 'Connection refused'))
```

**Solution:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# If not running, start it
ollama serve

# Verify it's accessible
curl http://localhost:11434/api/version
```

---

### Issue 2: "Model not found"

**Symptom:**
```
Error: model 'mistral:7b' not found
```

**Solution:**
```bash
# List available models
ollama list

# Pull the model
ollama pull mistral:7b

# Verify
ollama list | grep mistral
```

---

### Issue 3: API key not working

**Symptom:**
```
AuthenticationError: Invalid API key
```

**Solution:**
```bash
# Verify key is set
echo $OPENAI_API_KEY  # or $ANTHROPIC_API_KEY

# If empty, set it
export OPENAI_API_KEY="sk-..."

# Test the key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

### Issue 4: LLM Planning slow

**Symptoms:**
- Planning takes >30 seconds
- Terminal shows "generating..."

**Solutions:**

**Option 1: Use smaller model**
```python
llm_planner_local_model="mistral:7b-q4"  # Quantized version
```

**Option 2: Use API instead**
```python
llm_planner_local_model=None,
llm_planner_api_model="gpt-3.5-turbo",  # Faster than gpt-4
```

**Option 3: Disable planning for simple problems**
```python
# Only enable for complex problems
if complexity_score > 0.7:
    config.enable_llm_planning = True
```

---

### Issue 5: Auditing costs too much

**Solution:** Use cheaper models or mock mode

```python
# Option 1: Use cheaper model
auditor_backend='gpt',  # GPT-3.5 instead of Claude Opus

# Option 2: Only audit failed diagrams
if validation_report.has_errors():
    config.enable_llm_auditing = True
else:
    config.enable_llm_auditing = False

# Option 3: Use mock for development
auditor_backend='mock',
```

---

## Testing

### Test LLM Planning

```python
from unified_diagram_pipeline import UnifiedDiagramPipeline, PipelineConfig

config = PipelineConfig(
    enable_llm_planning=True,
    llm_planner_local_model="mistral:7b"
)

pipeline = UnifiedDiagramPipeline(config)

problem = "A block of mass 5 kg slides down an inclined plane at 30 degrees."
result = pipeline.generate(problem)

# Check if plan was generated
if result.llm_plan:
    print(f"✅ LLM Plan generated:")
    print(f"  Entities: {len(result.llm_plan['entities'])}")
    print(f"  Relationships: {len(result.llm_plan['relationships'])}")
else:
    print("❌ No LLM plan generated")
```

### Test LLM Auditing

```python
config = PipelineConfig(
    enable_llm_auditing=True,
    auditor_backend='claude',
    auditor_api_key=os.getenv('ANTHROPIC_API_KEY')
)

pipeline = UnifiedDiagramPipeline(config)
result = pipeline.generate(problem)

# Check audit results
if result.audit_report:
    print(f"✅ Audit completed:")
    print(f"  Score: {result.audit_report['overall_score']:.1f}/10")
    print(f"  Issues: {result.audit_report['issue_count']}")

    if result.audit_report['critical_issues']:
        print(f"  ⚠️  Critical issues found!")
else:
    print("❌ No audit report")
```

---

## Current Status

### What's Working

| Feature | Status | Default |
|---------|--------|---------|
| LLM Planning (Ollama) | ✅ Implemented | 🔴 Disabled |
| LLM Planning (OpenAI) | ✅ Implemented | 🔴 Disabled |
| LLM Auditing (Claude) | ✅ Implemented | 🔴 Disabled (mock active) |
| LLM Auditing (GPT) | ✅ Implemented | 🔴 Disabled (mock active) |
| LLM Auditing (Mock) | ✅ Implemented | 🟢 **Enabled** |
| Integration | ✅ Complete | - |
| Documentation | ✅ Complete | - |

### To Enable Real LLMs

**Just change these 2 lines in [api_server.py](api_server.py):**

```python
# Line 196: Enable LLM planning
enable_llm_planning=True,  # Changed from False

# Line 192: Change auditor backend
auditor_backend='claude',  # Changed from 'mock'
```

Then restart Flask!

---

## Next Steps

1. **Choose your LLM backend** (Ollama, OpenAI, Claude)
2. **Follow setup guide** for your chosen backend
3. **Update configuration** in api_server.py
4. **Restart Flask server**
5. **Test with a diagram**
6. **Monitor costs** (if using API)

---

## Support

**Issues?**
- Check [Troubleshooting](#troubleshooting) section
- Review Ollama logs: `ollama logs`
- Check Flask logs for errors
- Verify API keys are set correctly

**Questions?**
- Ollama: https://ollama.com/docs
- OpenAI: https://platform.openai.com/docs
- Anthropic: https://docs.anthropic.com/

---

**Last Updated:** November 10, 2025
**Status:** ✅ Production Ready
