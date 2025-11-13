# Installing Missing NLP Tools

**Date:** November 12, 2025

---

## 1. Stanza - Download English Models

Since Stanza is already installed, you just need to download the English models:

### Option A: Default Download
```bash
python3 -c "import stanza; stanza.download('en')"
```

### Option B: Custom Directory (if default fails with permissions)
```bash
# Set custom directory
export STANZA_RESOURCES_DIR="/tmp/claude/stanza_resources"

# Download models to custom directory
python3 -c "
import stanza
import os
os.environ['STANZA_RESOURCES_DIR'] = '/tmp/claude/stanza_resources'
stanza.download('en', model_dir='/tmp/claude/stanza_resources')
"
```

### Option C: Download Specific Components
```bash
python3 -c "
import stanza
# Download only what you need
stanza.download('en', processors='tokenize,pos,lemma,depparse,ner')
"
```

### Verify Installation
```bash
python3 -c "
import stanza
nlp = stanza.Pipeline('en', processors='tokenize,ner')
doc = nlp('A capacitor stores charge.')
print('✅ Stanza working!')
for ent in doc.entities:
    print(f'  {ent.text}: {ent.type}')
"
```

---

## 2. SciBERT - Download Model

SciBERT uses HuggingFace transformers. Download the model:

### Option A: Automatic Download (First Use)
```bash
python3 -c "
from transformers import AutoTokenizer, AutoModel

print('Downloading SciBERT model...')
tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')
print('✅ SciBERT downloaded successfully!')
"
```

### Option B: Download to Custom Cache Directory
```bash
# Set custom cache directory
export HF_HOME="/tmp/claude/huggingface"
export TRANSFORMERS_CACHE="/tmp/claude/huggingface"

python3 -c "
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')
print('✅ SciBERT downloaded to custom directory!')
"
```

### Option C: Manual Download (if network restricted)
```bash
# 1. Visit: https://huggingface.co/allenai/scibert_scivocab_uncased
# 2. Click "Files and versions"
# 3. Download these files:
#    - config.json
#    - pytorch_model.bin
#    - vocab.txt
#    - tokenizer_config.json
#    - special_tokens_map.json
# 4. Save to: ~/.cache/huggingface/hub/models--allenai--scibert_scivocab_uncased/

# Or use git-lfs:
cd ~/.cache/huggingface/hub/
git lfs install
git clone https://huggingface.co/allenai/scibert_scivocab_uncased
```

### Verify Installation
```bash
python3 -c "
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')

text = 'The capacitor has capacitance C.'
tokens = tokenizer(text, return_tensors='pt')
outputs = model(**tokens)

print('✅ SciBERT working!')
print(f'   Embedding shape: {outputs.last_hidden_state.shape}')
"
```

---

## 3. DyGIE++ (AllenNLP) - Install Package

DyGIE++ requires AllenNLP, which may not be available in recent versions.

### Option A: Try Latest AllenNLP
```bash
pip install allennlp allennlp-models
```

### Option B: Try Without Version Constraint
```bash
pip install allennlp
```

### Option C: Use Alternative (Skip DyGIE++)

Since AllenNLP 2.10.1 doesn't exist and newer versions may have breaking changes, **consider skipping DyGIE++**. The pipeline works great with the other 6 NLP tools!

To disable DyGIE++:
```python
# In your config
config.nlp_tools = ['openie', 'stanza', 'scibert', 'chemdataextractor', 'mathbert', 'amr']
# Removed 'dygie'
```

### Option D: Check What's Actually Needed

Let me check if DyGIE++ is actually used:

```bash
python3 -c "
from core.nlp_tools.dygie_extractor import DyGIEExtractor
# If this imports, AllenNLP is available
print('✅ DyGIE++ dependencies available')
"
```

If you see `ImportError: AllenNLP not installed`, try:

```bash
# Check available versions
pip index versions allennlp

# Install latest available
pip install allennlp --no-cache-dir
```

---

## Quick Installation Script

Run this to attempt all installations:

```bash
#!/bin/bash

echo "=================================================="
echo "Installing NLP Tools for STEM AI Pipeline"
echo "=================================================="

# 1. Stanza models
echo -e "\n1. Downloading Stanza English models..."
python3 -c "
import stanza
try:
    stanza.download('en')
    print('✅ Stanza models downloaded')
except Exception as e:
    print(f'❌ Stanza download failed: {e}')
" 2>&1 | grep -E "✅|❌"

# 2. SciBERT
echo -e "\n2. Downloading SciBERT model..."
python3 -c "
from transformers import AutoTokenizer, AutoModel
try:
    tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
    model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')
    print('✅ SciBERT model downloaded')
except Exception as e:
    print(f'❌ SciBERT download failed: {e}')
" 2>&1 | grep -E "✅|❌"

# 3. AllenNLP (for DyGIE++)
echo -e "\n3. Installing AllenNLP..."
pip install allennlp 2>&1 | grep -E "Successfully installed|ERROR|already satisfied"
if [ $? -eq 0 ]; then
    echo "✅ AllenNLP installed"
else
    echo "❌ AllenNLP installation failed"
fi

echo -e "\n=================================================="
echo "Installation Complete!"
echo "=================================================="

# Verify all tools
python3 -c "
print('\nVerifying NLP tools...\n')

# OpenIE
try:
    from core.nlp_tools.openie_extractor import OpenIEExtractor
    print('✅ OpenIE: Available')
except:
    print('❌ OpenIE: Not available')

# Stanza
try:
    from core.nlp_tools.stanza_enhancer import StanzaEnhancer
    StanzaEnhancer()
    print('✅ Stanza: Available (with models)')
except Exception as e:
    print(f'❌ Stanza: Not available - {type(e).__name__}')

# SciBERT
try:
    from core.nlp_tools.scibert_embedder import SciBERTEmbedder
    SciBERTEmbedder()
    print('✅ SciBERT: Available (with models)')
except Exception as e:
    print(f'❌ SciBERT: Not available - {type(e).__name__}')

# DyGIE++
try:
    from core.nlp_tools.dygie_extractor import DyGIEExtractor
    print('✅ DyGIE++: Available')
except Exception as e:
    print(f'❌ DyGIE++: Not available - {type(e).__name__}')

# ChemDataExtractor
try:
    from core.nlp_tools.chemdataextractor_parser import ChemDataExtractorParser
    print('✅ ChemDataExtractor: Available')
except:
    print('❌ ChemDataExtractor: Not available')

# MathBERT
try:
    from core.nlp_tools.mathbert_extractor import MathBERTExtractor
    print('✅ MathBERT: Available')
except:
    print('❌ MathBERT: Not available')

# AMR
try:
    from core.nlp_tools.amr_parser import AMRParser
    print('✅ AMR Parser: Available')
except:
    print('❌ AMR Parser: Not available')
"
```

Save this as `install_nlp_tools.sh` and run:
```bash
chmod +x install_nlp_tools.sh
./install_nlp_tools.sh
```

---

## Troubleshooting

### Stanza: "Resources file not found"

**Problem:** Permission error creating `/Users/Pramod/stanza_resources`

**Solution 1:** Use custom directory
```bash
mkdir -p ~/Documents/stanza_resources
export STANZA_RESOURCES_DIR=~/Documents/stanza_resources
python3 -c "import stanza; stanza.download('en')"
```

**Solution 2:** Use /tmp
```bash
export STANZA_RESOURCES_DIR=/tmp/claude/stanza_resources
mkdir -p /tmp/claude/stanza_resources
python3 -c "import stanza; stanza.download('en')"
```

Then update the Stanza enhancer to use this directory:
```python
# In core/nlp_tools/stanza_enhancer.py
import os
os.environ['STANZA_RESOURCES_DIR'] = '/tmp/claude/stanza_resources'
```

---

### SciBERT: "ProxyError"

**Problem:** Network proxy blocking HuggingFace

**Solution 1:** Disable proxy temporarily
```bash
unset HTTP_PROXY HTTPS_PROXY
python3 -c "from transformers import AutoModel; AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')"
```

**Solution 2:** Use VPN or different network

**Solution 3:** Manual download (see Option C above)

---

### DyGIE++: "AllenNLP not installed"

**Problem:** AllenNLP 2.10.1 doesn't exist

**Solution 1:** Try without version
```bash
pip install allennlp
```

**Solution 2:** Skip DyGIE++ (recommended)
It's optional - remove from config:
```python
config.nlp_tools = ['openie', 'stanza', 'scibert', 'chemdataextractor', 'mathbert', 'amr']
```

**Solution 3:** Use spaCy as alternative
DyGIE++ does entity extraction, which spaCy also does:
```bash
pip install spacy
python3 -m spacy download en_core_web_sm
```

---

## After Installation

### Test the Pipeline

```bash
python3 test_all_features.py
```

**Expected output:**
```
✓ Phase 0.5: OpenIE [ACTIVE]
✓ Phase 0.5: Stanza [ACTIVE]              # After Stanza models downloaded
✓ Phase 0.5: SciBERT [ACTIVE]             # After SciBERT model downloaded
✓ Phase 0.5: ChemDataExtractor [ACTIVE]
✓ Phase 0.5: MathBERT [ACTIVE]
✓ Phase 0.5: AMR Parser [ACTIVE]
⚠ Phase 0.5: DyGIE++ [FAILED]             # Optional - can skip
```

### Check Trace Output

After running, check the latest trace:
```bash
python3 -c "
import json
from pathlib import Path

traces = sorted(Path('logs').glob('*_trace.json'), key=lambda p: p.stat().st_mtime, reverse=True)
if traces:
    with open(traces[0]) as f:
        trace = json.load(f)

    for phase in trace['phases']:
        if 'NLP' in phase['phase_name']:
            output = phase.get('output', {})
            print(f'NLP tools with output: {list(output.keys())}')
            print(f'Tool count: {len(output)}')
            break
"
```

**Expected:** 5-6 tools (OpenIE, Stanza, SciBERT, ChemDataExtractor, MathBERT, AMR)

---

## Summary

| Tool | Installation Command | Required? |
|------|---------------------|-----------|
| OpenIE | (already working) | ✅ Core |
| ChemDataExtractor | (already working) | ✅ Core |
| MathBERT | (already working) | ✅ Core |
| AMR Parser | (already working) | ✅ Core |
| **Stanza** | `python3 -c "import stanza; stanza.download('en')"` | ⭐ Recommended |
| **SciBERT** | `from transformers import AutoModel; AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')` | ⭐ Recommended |
| **DyGIE++** | `pip install allennlp` (or skip) | ⚪ Optional |

**Minimum working:** 4 tools (already functional)
**Recommended:** 6 tools (add Stanza + SciBERT)
**Maximum:** 7 tools (add DyGIE++ if AllenNLP available)

---

**Next Steps:**

1. Run the installation script above
2. Test with `python3 test_all_features.py`
3. Check trace to see which tools produced output
4. Enjoy the full NLP stack! 🎉
