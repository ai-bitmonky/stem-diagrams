#!/bin/bash

echo "=================================================="
echo "Installing NLP Tools for STEM AI Pipeline"
echo "=================================================="

# 1. Stanza models
echo -e "\n[1/3] Downloading Stanza English models..."
python3 -c "
import stanza
try:
    stanza.download('en')
    print('✅ Stanza models downloaded successfully')
except Exception as e:
    print(f'❌ Stanza download failed: {type(e).__name__}: {str(e)[:100]}')
    print('   Try: export STANZA_RESOURCES_DIR=/tmp/claude/stanza_resources')
"

# 2. SciBERT
echo -e "\n[2/3] Downloading SciBERT model (this may take a few minutes)..."
python3 -c "
from transformers import AutoTokenizer, AutoModel
try:
    print('  Downloading tokenizer...')
    tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
    print('  Downloading model...')
    model = AutoModel.from_pretrained('allenai/scibert_scivocab_uncased')
    print('✅ SciBERT model downloaded successfully')
except Exception as e:
    print(f'❌ SciBERT download failed: {type(e).__name__}: {str(e)[:100]}')
    print('   This is likely a network/proxy issue')
"

# 3. AllenNLP (for DyGIE++)
echo -e "\n[3/3] Installing AllenNLP (optional)..."
pip install allennlp 2>&1 | grep -E "Successfully installed|already satisfied|ERROR" | head -5
if [ $? -eq 0 ]; then
    echo "✅ AllenNLP check complete"
else
    echo "⚠️  AllenNLP installation may have failed (this is optional)"
fi

echo -e "\n=================================================="
echo "Installation Complete! Verifying..."
echo "=================================================="

# Verify all tools
python3 << 'PYTHON_VERIFY'
import sys

print('\nNLP Tools Status:\n')

results = []

# Test each tool
tools = {
    'OpenIE': 'core.nlp_tools.openie_extractor.OpenIEExtractor',
    'Stanza': 'core.nlp_tools.stanza_enhancer.StanzaEnhancer',
    'SciBERT': 'core.nlp_tools.scibert_embedder.SciBERTEmbedder',
    'DyGIE++': 'core.nlp_tools.dygie_extractor.DyGIEExtractor',
    'ChemDataExtractor': 'core.nlp_tools.chemdataextractor_parser.ChemDataExtractorParser',
    'MathBERT': 'core.nlp_tools.mathbert_extractor.MathBERTExtractor',
    'AMR Parser': 'core.nlp_tools.amr_parser.AMRParser'
}

for name, import_path in tools.items():
    try:
        module_path, class_name = import_path.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)

        # Try to instantiate
        try:
            instance = cls()
            print(f'✅ {name:20s} : Available and working')
            results.append((name, True, None))
        except Exception as e:
            print(f'⚠️  {name:20s} : Available but initialization failed')
            print(f'    Error: {type(e).__name__}: {str(e)[:60]}')
            results.append((name, False, type(e).__name__))
    except ImportError as e:
        print(f'❌ {name:20s} : Not available (import failed)')
        results.append((name, False, 'ImportError'))

print('\n' + '='*50)
print('Summary:')
print('='*50)

working = [r[0] for r in results if r[1]]
failed = [r[0] for r in results if not r[1]]

print(f'Working tools: {len(working)}/7')
if working:
    print(f'  ✅ {", ".join(working)}')

if failed:
    print(f'\nFailed tools: {len(failed)}/7')
    print(f'  ❌ {", ".join(failed)}')

print('\n' + '='*50)

if len(working) >= 4:
    print('✅ Pipeline is operational!')
    print(f'   {len(working)} NLP tools are working.')
    if len(working) < 7:
        print(f'   {len(failed)} tools need setup (see INSTALL_NLP_TOOLS.md)')
else:
    print('⚠️  Some issues detected. Check errors above.')

print('='*50)
PYTHON_VERIFY

echo -e "\nFor detailed installation instructions, see:"
echo "  INSTALL_NLP_TOOLS.md"
echo ""
echo "To test the pipeline, run:"
echo "  python3 test_all_features.py"
echo ""
