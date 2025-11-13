"""FastAPI server for the Unified Diagram Pipeline.

This replaces the legacy Flask wrapper with a production-ready FastAPI
entrypoint that can be served by Uvicorn/Gunicorn workers. The core pipeline
logic remains untouched – we simply expose `/api/generate` and `/api/health`
endpoints with structured logging and typed request/response models.
"""

from __future__ import annotations

import logging
import os
import sys
import time
import uuid
from functools import lru_cache
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from unified_diagram_pipeline import PipelineConfig, UnifiedDiagramPipeline


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOGGER = logging.getLogger("fastapi_server")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)
LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Request / Response Schemas
# ---------------------------------------------------------------------------


class GenerateRequest(BaseModel):
    problem_text: str = Field(..., min_length=4, description="STEM problem prompt")


class DiagramMetadata(BaseModel):
    complexity_score: float
    selected_strategy: str
    property_graph_nodes: int
    property_graph_edges: int
    ontology_validation: Optional[Dict[str, Any]] = None
    nlp_tools_used: List[str] = []


class GenerateResponse(BaseModel):
    request_id: str
    svg: str
    metadata: DiagramMetadata


class HealthResponse(BaseModel):
    status: str
    pipeline: str
    features: Dict[str, Any]
    uptime_seconds: float


# ---------------------------------------------------------------------------
# Pipeline Factory (EAGER initialization at startup, not lazy)
# ---------------------------------------------------------------------------

# Global pipeline instance - initialized at server startup
_pipeline: Optional[UnifiedDiagramPipeline] = None


def initialize_pipeline() -> UnifiedDiagramPipeline:
    """Initialize pipeline at server startup with NLP model warmup"""
    LOGGER.info("Initializing UnifiedDiagramPipeline via FastAPI server…")

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key:
        LOGGER.info("DeepSeek API key detected (prefix=%s)", api_key[:7])
    else:
        LOGGER.warning("DeepSeek API key missing – LLM features disabled")

    config = PipelineConfig(
        api_key=api_key,
        api_base_url="https://api.deepseek.com",
        api_model="deepseek-chat",
        validation_mode="standard",
        enable_layout_optimization=True,
        enable_domain_embellishments=True,
        enable_ai_validation=False,
        enable_property_graph=True,
        enable_nlp_enrichment=True,
        enable_nlp_warmup=True,  # CRITICAL: Enable warmup at startup
        nlp_tools=["openie", "stanza", "dygie", "scibert", "chemdataextractor", "mathbert", "amr"],
        enable_llm_planning=bool(api_key),
        llm_planner_api_model="deepseek-chat",
        enable_llm_auditing=bool(api_key),
        auditor_backend="deepseek" if api_key else "mock",
        auditor_api_key=api_key,
        enable_deepseek_enrichment=bool(api_key),
        enable_deepseek_audit=bool(api_key),
        enable_deepseek_validation=bool(api_key),
        deepseek_api_key=api_key,
        deepseek_model="deepseek-chat",
        deepseek_base_url="https://api.deepseek.com",
    )

    try:
        pipeline = UnifiedDiagramPipeline(config)
        LOGGER.info("UnifiedDiagramPipeline ready with features: %s", config.nlp_tools)
    except Exception as exc:  # pragma: no cover - initialization failure is fatal
        LOGGER.exception("Failed to initialize pipeline: %s", exc)
        raise

    return pipeline


def get_pipeline() -> UnifiedDiagramPipeline:
    """Get the pre-initialized pipeline instance"""
    if _pipeline is None:
        raise RuntimeError("Pipeline not initialized - server startup may have failed")
    return _pipeline


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------


app = FastAPI(title="STEM Diagram Generator", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()


@app.on_event("startup")
async def startup_event():
    """Initialize pipeline with NLP model warmup at server startup"""
    global _pipeline
    LOGGER.info("Server startup: Initializing pipeline with NLP warmup...")
    _pipeline = initialize_pipeline()
    LOGGER.info("Server startup complete: Pipeline ready for requests")


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_diagram(request: Request, payload: GenerateRequest) -> GenerateResponse:
    pipeline = get_pipeline()
    req_id = str(uuid.uuid4())

    LOGGER.info("[%s] /api/generate received (%d chars)", req_id, len(payload.problem_text))

    try:
        result = pipeline.generate(payload.problem_text)
    except Exception as exc:
        LOGGER.exception("[%s] Pipeline execution failed", req_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    metadata = DiagramMetadata(
        complexity_score=getattr(result, "complexity_score", 0.0) or 0.0,
        selected_strategy=getattr(result, "selected_strategy", "unknown") or "unknown",
        property_graph_nodes=len(result.property_graph.get_all_nodes()) if result.property_graph else 0,
        property_graph_edges=len(result.property_graph.get_edges()) if result.property_graph else 0,
        ontology_validation=getattr(result, "ontology_validation", None),
        nlp_tools_used=list(result.nlp_results.keys()) if result.nlp_results else [],
    )

    LOGGER.info(
        "[%s] completed complexity=%.3f strategy=%s nodes=%d edges=%d",
        req_id,
        metadata.complexity_score,
        metadata.selected_strategy,
        metadata.property_graph_nodes,
        metadata.property_graph_edges,
    )

    return GenerateResponse(request_id=req_id, svg=result.svg, metadata=metadata)


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    pipeline = get_pipeline()
    uptime = time.time() - START_TIME

    feature_flags = {
        "property_graph": bool(pipeline.property_graph),
        "nlp_enrichment": bool(pipeline.nlp_tools),
        "diagram_planner": bool(pipeline.diagram_planner),
        "llm_planner": bool(pipeline.llm_planner),
        "llm_auditor": bool(pipeline.auditor),
    }

    return HealthResponse(
        status="ok",
        pipeline="unified_diagram_pipeline.py",
        features=feature_flags,
        uptime_seconds=uptime,
    )


if __name__ == "__main__":  # pragma: no cover - manual launch helper
    try:
        import uvicorn
    except ImportError as exc:
        LOGGER.error("uvicorn is required to run the FastAPI server: %s", exc)
        sys.exit(1)

    LOGGER.info("Starting Uvicorn server on http://0.0.0.0:8000 …")
    uvicorn.run("fastapi_server:app", host="0.0.0.0", port=8000, reload=False)
