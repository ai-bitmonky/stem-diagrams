# Pipeline Tracing and Logging System

**Date:** November 17, 2025
**Version:** 1.0
**Purpose:** Comprehensive input/output tracking for diagram generation pipeline

---

## Overview

The pipeline tracing system provides detailed logging and tracking of every component in the diagram generation pipeline. It captures:

- Input data at each phase
- Output data from each component
- Entity-level transformations (additions, deletions, modifications)
- Performance metrics
- Error and warning aggregation
- Entity lifecycle tracking

---

## Architecture

### Core Components

1. **PipelineTracer** (`core/pipeline_tracer.py`)
   - Main tracing orchestrator
   - Manages component traces
   - Tracks entity flow
   - Aggregates errors/warnings
   - Exports comprehensive JSON traces

2. **ComponentTrace** (dataclass)
   - Individual component execution record
   - Tracks inputs, outputs, transformations
   - Performance timing
   - Error/warning collection

### Integration Points

The tracer is integrated at these critical phases:

1. **Phase 0: NLP Enrichment**
   - Input: Problem text
   - Output: NLP extraction results (OpenIE, Stanza, SciBERT, etc.)
   - Tracks: Extraction time per tool, entity counts

2. **Phase 0.5: Property Graph Construction**
   - Input: NLP results
   - Output: Property graph with nodes and edges
   - Tracks: Every entity addition with source attribution
   - **Critical for debugging garbage entities**

3. **Phase 0.6: DeepSeek Enrichment** (when enabled)
   - Input: Raw property graph
   - Output: Enriched/filtered entities
   - Tracks: Entities added, filtered, modified

4. **Additional phases** can be instrumented similarly

---

## Usage

### Automatic Tracing

Tracing is **automatically enabled** for all diagram generation requests. No configuration needed.

### Output Files

For each request with ID `req_YYYYMMDD_HHMMSS`, the following files are generated:

1. **Detailed Trace**: `logs/req_YYYYMMDD_HHMMSS_detailed_trace.json`
   - Complete component-level tracing
   - Entity lifecycle
   - Transformation logs
   - Error/warning aggregation

2. **Original Trace**: `generation_trace.json`
   - Legacy trace format (kept for compatibility)

### Trace File Structure

```json
{
  "request_id": "req_20251117_100407",
  "timestamp": "2025-11-17T10:04:09",
  "total_duration_ms": 1234.56,
  "components": [
    {
      "component_name": "NLP Enrichment",
      "phase": "Phase 0",
      "start_time": 1700123456.789,
      "end_time": 1700123457.123,
      "duration_ms": 334.0,
      "input_summary": {
        "type": "str",
        "length": 366,
        "preview": "A potential difference of 300 V..."
      },
      "output_summary": {
        "type": "dict",
        "keys": ["openie", "stanza", "scibert", "chemdataextractor"],
        "key_count": 4
      },
      "transformations": [
        {
          "type": "NLP Extraction",
          "timestamp": 1700123457.0,
          "details": {
            "tools_used": ["openie", "stanza", "scibert", "chemdataextractor"],
            "total_time_ms": 334.0
          }
        }
      ],
      "added_count": 0,
      "filtered_count": 0,
      "modified_count": 0,
      "errors": [],
      "warnings": []
    },
    {
      "component_name": "Property Graph Construction",
      "phase": "Phase 0.5",
      "added_count": 10,
      "filtered_count": 0,
      "modified_count": 0,
      ...
    }
  ],
  "entity_lifecycle": {
    "300 V": [
      "added_in_Phase 0.5",
      "validated_in_Phase 0.6"
    ],
    "What is": [
      "added_in_Phase 0.5",
      "filtered_in_Phase 0.6: Not a physical entity"
    ]
  },
  "entity_flow": [
    {
      "phase": "Property Graph Construction",
      "timestamp": 1700123457.5,
      "entity_count": 10,
      "entities": [
        {"id": "300 V", "type": "OBJECT", "label": "300 V"},
        {"id": "What is", "type": "OBJECT", "label": "What is"}
      ]
    }
  ],
  "errors": [],
  "warnings": [],
  "summary": {
    "total_components": 5,
    "total_errors": 0,
    "total_warnings": 2,
    "total_entities_added": 10,
    "total_entities_filtered": 0,
    "total_entities_modified": 0
  }
}
```

---

## Key Features

### 1. Entity-Level Tracking

Every entity added to the property graph is logged with:

```python
tracer.log_entity_added("300 V", {
    'source': 'OpenIE',
    'type': 'OBJECT',
    'label': '300 V',
    'relation_role': 'object',
    'relation': 'is applied to'
})
```

**Output:**
```
   ➕ ADDED: 300 V
      Data: {
        "source": "OpenIE",
        "type": "OBJECT",
        "label": "300 V",
        "relation_role": "object",
        "relation": "is applied to"
      }
```

### 2. Entity Filtering

When entities are filtered/removed:

```python
tracer.log_entity_filtered("What is", "Not a physical entity - question phrase")
```

**Output:**
```
   ❌ FILTERED: What is
      Reason: Not a physical entity - question phrase
```

### 3. Entity Modification

When entities are enriched/modified:

```python
tracer.log_entity_modified("300 V", {
    'added_type': 'voltage',
    'added_properties': {'unit': 'V', 'value': 300}
})
```

**Output:**
```
   ✏️  MODIFIED: 300 V
      Changes: {
        "added_type": "voltage",
        "added_properties": {"unit": "V", "value": 300}
      }
```

### 4. Entity Lifecycle Tracking

The tracer maintains a complete lifecycle for each entity across all phases:

```json
"entity_lifecycle": {
  "capacitor C₁": [
    "added_in_Phase 0.5",
    "validated_in_Phase 0.6",
    "enriched_in_Phase 0.6: Added capacitance property",
    "rendered_in_Phase 6"
  ]
}
```

### 5. Console Output

Real-time console output shows execution flow:

```
================================================================================
🔍 TRACE START: Property Graph Construction (Phase: Phase 0.5)
================================================================================

📥 INPUT: nlp_results
   Type: dict
   Summary: {
     "type": "dict",
     "keys": ["openie", "stanza", "scibert", "chemdataextractor"],
     "key_count": 4
   }

   ➕ ADDED: 300 V
      Data: {"source": "OpenIE", "type": "OBJECT", ...}

   ➕ ADDED: capacitor C₁
      Data: {"source": "Stanza", "type": "OBJECT", ...}

   ➕ ADDED: What is
      Data: {"source": "OpenIE", "type": "OBJECT", ...}

📤 OUTPUT: property_graph
   Type: dict
   Summary: {
     "total_nodes": 10,
     "total_edges": 5
   }

🔄 TRANSFORMATION: Property Graph Construction
   Details: {
     "sources_used": ["OpenIE", "Stanza", "SciBERT"],
     "total_nodes": 10,
     "total_edges": 5
   }

================================================================================
✅ TRACE COMPLETE: Property Graph Construction
   Duration: 5.23ms
   Added: 10
   Filtered: 0
   Modified: 0
   Errors: 0
   Warnings: 0
================================================================================
```

---

## Debugging Workflow

### Problem: Garbage Entities in Diagrams

**Step 1: Check Entity Flow**

```bash
# Look at detailed trace
cat logs/req_*_detailed_trace.json | python3 -m json.tool | grep -A 20 "entity_flow"
```

**Step 2: Identify Source of Garbage**

```json
"entity_flow": [
  {
    "phase": "Property Graph Construction",
    "entities": [
      {"id": "What is", "label": "What is", "type": "OBJECT"},  // ❌ Garbage
      {"id": "They are", "label": "They are", "type": "OBJECT"}  // ❌ Garbage
    ]
  }
]
```

**Step 3: Check Entity Lifecycle**

```json
"entity_lifecycle": {
  "What is": [
    "added_in_Phase 0.5"
    // ❌ Should have been filtered in Phase 0.6 but wasn't
  ]
}
```

**Step 4: Find Root Cause**

Look at component traces for Phase 0.5:

```json
"components": [
  {
    "component_name": "Property Graph Construction",
    "phase": "Phase 0.5",
    "added_count": 10,  // Total entities added
    "filtered_count": 0,  // ❌ Nothing was filtered
    ...
  }
]
```

**Root Cause:** No filtering happening in Property Graph Construction phase

**Solution:** Add entity filter after property graph construction (see DIAGRAM_ACCURACY_ROOT_CAUSE.md)

---

## Performance Analysis

The trace includes timing breakdown:

```json
"phase_times": {
  "NLP Enrichment": 334.0,
  "Property Graph Construction": 5.23,
  "DeepSeek Enrichment": 325.38,
  "Scene Building": 170.69
}
```

**Summary at end:**
```
📊 PIPELINE EXECUTION SUMMARY
================================================================================
Request ID: req_20251117_100407
Total Duration: 1234.56ms

📈 Entity Flow:
   Total Added: 10
   Total Filtered: 0
   Total Modified: 0

⏱️  Phase Breakdown:
   NLP Enrichment: 334.00ms
   Property Graph Construction: 5.23ms
   DeepSeek Enrichment: 325.38ms
   ...
```

---

## Error Aggregation

All errors across all phases are collected:

```json
"errors": [
  {
    "timestamp": 1700123457.8,
    "component": "DeepSeek Enrichment",
    "phase": "Phase 0.6",
    "error": "Authentication Fails, Your api key: ****b9bc is invalid",
    "context": {}
  }
]
```

---

## Adding Tracing to New Components

### Template

```python
# Start component trace
tracer.start_component("Component Name", "Phase X", {
    'metadata_key': 'metadata_value'
})

# Log input
tracer.log_input(input_data, "input_description")

# ... component logic ...

# Log entity operations
tracer.log_entity_added(entity_id, entity_data)
tracer.log_entity_filtered(entity_id, reason)
tracer.log_entity_modified(entity_id, changes)

# Log transformations
tracer.log_transformation("Transformation Type", {
    'detail_key': 'detail_value'
})

# Log errors/warnings
tracer.log_error("Error message", context_dict)
tracer.log_warning("Warning message", context_dict)

# Log output
tracer.log_output(output_data, "output_description")

# Complete trace
tracer.complete_component()
```

### Example: Adding Trace to Scene Builder

```python
# In unified_diagram_pipeline.py, Scene Building phase

tracer.start_component("Scene Building", "Phase 3", {
    'domain': domain,
    'entity_count': len(entities)
})

tracer.log_input(entities, "entities_from_property_graph")

# Build scene
scene = scene_builder.build(entities)

tracer.log_output(scene, "generated_scene")
tracer.log_transformation("Scene Building", {
    'input_entities': len(entities),
    'output_objects': len(scene.objects),
    'filtered': len(entities) - len(scene.objects)
})

tracer.complete_component()
```

---

## Benefits

1. **Complete Visibility** - See exactly what happens at every stage
2. **Entity Provenance** - Track where each entity comes from
3. **Error Diagnosis** - Quickly identify which phase failed and why
4. **Performance Optimization** - Identify bottlenecks
5. **Quality Debugging** - Understand why diagrams are inaccurate
6. **Historical Analysis** - Compare traces across requests

---

## Future Enhancements

1. **Web UI** - Visual trace viewer (timeline, entity graph)
2. **Trace Comparison** - Diff two traces to see what changed
3. **Automatic Anomaly Detection** - Flag unusual patterns
4. **Entity Flow Visualization** - Sankey diagram of entity transformations
5. **Performance Regression Detection** - Alert when phases slow down

---

## Summary

The pipeline tracing system provides **comprehensive visibility** into every aspect of diagram generation. It's particularly valuable for:

- **Debugging accuracy issues** (garbage entities, missing components)
- **Performance optimization** (identify slow phases)
- **Quality improvement** (understand transformation pipeline)
- **Error diagnosis** (pinpoint failure points)

**Key Takeaway:** Every entity addition, filtering, and modification is now logged, making it trivial to understand why diagrams are inaccurate.

---

**Next Steps:**
1. Run a diagram generation request
2. Check `logs/req_*_detailed_trace.json`
3. Analyze entity flow to identify garbage entities
4. Implement filtering based on findings
