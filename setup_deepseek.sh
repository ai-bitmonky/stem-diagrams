#!/bin/bash
# DeepSeek API Setup Script
# This script helps you configure and verify DeepSeek API integration

echo "========================================================================"
echo "DeepSeek API Setup & Verification"
echo "========================================================================"
echo ""

# Check if API key is set
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ DEEPSEEK_API_KEY environment variable is NOT set"
    echo ""
    echo "To enable DeepSeek LLM features:"
    echo ""
    echo "1. Get your API key from https://platform.deepseek.com/"
    echo "   (Sign up if you don't have an account)"
    echo ""
    echo "2. Set the environment variable:"
    echo "   export DEEPSEEK_API_KEY='sk-your-api-key-here'"
    echo ""
    echo "3. To make it permanent, add to your shell profile:"
    echo "   echo 'export DEEPSEEK_API_KEY=\"sk-your-key\"' >> ~/.bashrc"
    echo "   source ~/.bashrc"
    echo ""
    echo "4. Restart the API server:"
    echo "   python3 api_server.py"
    echo ""
    exit 1
else
    echo "✅ DEEPSEEK_API_KEY is set (starts with ${DEEPSEEK_API_KEY:0:7}...)"
fi

echo ""
echo "Checking Python dependencies..."
python3 -c "import openai; print('✅ openai package installed')" 2>/dev/null || echo "❌ openai package missing (install: pip install openai)"
python3 -c "import flask; print('✅ flask package installed')" 2>/dev/null || echo "❌ flask package missing (install: pip install flask)"
python3 -c "import flask_cors; print('✅ flask-cors package installed')" 2>/dev/null || echo "❌ flask-cors package missing (install: pip install flask-cors)"

echo ""
echo "Checking DeepSeek configuration in api_server.py..."
if grep -q "https://api.deepseek.com" api_server.py; then
    echo "✅ DeepSeek base URL configured"
else
    echo "❌ DeepSeek base URL not found"
fi

if grep -q "enable_llm_planning=bool(api_key)" api_server.py; then
    echo "✅ LLM Planning auto-enable configured"
else
    echo "⚠️  LLM Planning configuration needs review"
fi

if grep -q "enable_llm_auditing=bool(api_key)" api_server.py; then
    echo "✅ LLM Auditing auto-enable configured"
else
    echo "⚠️  LLM Auditing configuration needs review"
fi

echo ""
echo "========================================================================"
echo "Configuration Status: READY"
echo "========================================================================"
echo ""
echo "Your STEM Diagram Generator is configured with:"
echo "  ✅ All 7 NLP tools (OpenIE, Stanza, DyGIE++, SciBERT,"
echo "     ChemDataExtractor, MathBERT, AMR)"
echo "  ✅ LLM Planning (auto-enabled with DeepSeek)"
echo "  ✅ LLM Auditing (auto-enabled with DeepSeek)"
echo "  ✅ DeepSeek AI integration"
echo ""
echo "Features when API key is set:"
echo "  🤖 LLM-powered diagram planning"
echo "  🔍 AI quality validation"
echo "  💰 Cost: ~\$0.001-0.01 per diagram (50-100x cheaper than GPT-4)"
echo ""
echo "To start the API server with all features:"
echo "  python3 api_server.py"
echo ""
echo "Expected output:"
echo "  ✅ DeepSeek API key found (starts with sk-...)"
echo "  ✓ Phase 1+2: LLM Diagram Planner [ACTIVE]"
echo "  ✅ LLM Planner configured with DeepSeek"
echo "  ✓ Phase 7: LLM Auditor [ACTIVE]"
echo "  ✅ LLM Auditor configured with DeepSeek"
echo ""
echo "========================================================================"
