# Domain Module Framework

Pluggable builders for domain-specific rendering stacks:

| Domain | Module ID | Backend | Notes |
| --- | --- | --- | --- |
| Electronics | `electronics_schemdraw` | SchemDraw / CircuitikZ | Generates Python + LaTeX snippets for circuits. Works even if SchemDraw is not installed (template only). |
| Mechanics | `mechanics_pysketcher` | PySketcher / pyfreebody | Produces block/spring/force scaffolds. Falls back to script text when PySketcher is unavailable. |
| Chemistry | `chemistry_rdkit` | RDKit | Emits RDKit code for molecules detected in the plan (SMILES/SMARTS). |
| Biology | `biology_cytoscape` | Cytoscape JSON | Creates Cytoscape-compatible JSON networks for pathways/relations. |
| Computer Science | `cs_plantuml` | PlantUML / Mermaid | Generates textual templates for CS diagrams (class/flow graphs). |

## How it works
1. `DomainModuleRegistry` auto-registers the modules above (and any new ones placed under `core/domain_modules/`).
2. After the property-graph-driven `DiagramPlan` is created, the pipeline calls `DomainModuleRegistry.build_artifacts(...)` with the resolved domain.
3. Each module inspects the plan entities/relations and emits a `DomainModuleArtifact` (format, content, metadata).
4. Artifacts are stored on both the `CanonicalProblemSpec.diagram_plan_metadata` and the final `DiagramResult.domain_module_outputs`, so downstream tooling or the UI can surface them.

## Adding new modules
Implement `DomainModule` (see `core/domain_modules/base.py`) and register it with `DomainModuleRegistry.register(...)`. No changes to the main pipeline are required—new modules automatically participate once registered.

## Primitive Library Integration
Each domain module now queries the shared `PrimitiveLibrary` first. If a matching component is found (via Milvus/Qdrant/memory similarity search), the module assembles an SVG from those reusable parts and records `primitive_matches` in its metadata. When no suitable primitive is found, the module falls back to its procedural renderer (SchemDraw, PySketcher, RDKit, Cytoscape JSON, PlantUML/Mermaid). New primitives can be added to `core/primitive_library.py` or indexed in an external vector DB without changing module code.
