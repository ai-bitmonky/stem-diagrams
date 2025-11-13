"""Structural validation utilities for comparing DiagramPlan and rendered Scene."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.scene.schema_v1 import Scene


@dataclass
class StructuralComparison:
    missing_in_scene: List[str] = field(default_factory=list)
    extra_scene_objects: List[str] = field(default_factory=list)
    label_mismatches: List[str] = field(default_factory=list)
    relation_gaps: List[str] = field(default_factory=list)
    score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'missing_in_scene': self.missing_in_scene,
            'extra_scene_objects': self.extra_scene_objects,
            'label_mismatches': self.label_mismatches,
            'relation_gaps': self.relation_gaps,
            'score': self.score,
        }


def compare_plan_scene(diagram_plan: Any, scene: Scene) -> StructuralComparison:
    comparison = StructuralComparison()
    if not diagram_plan or not scene:
        return comparison

    plan_entities = _extract_plan_entities(diagram_plan)
    scene_objects = {obj.id: obj for obj in scene.objects if getattr(obj, 'id', None)}

    matched_scene_ids: set[str] = set()

    for entity_id, entity in plan_entities.items():
        scene_obj = scene_objects.get(entity_id)
        if scene_obj:
            matched_scene_ids.add(scene_obj.id)
            label = entity.get('label')
            scene_label = scene_obj.properties.get('label') if scene_obj.properties else None
            if label and scene_label and label.lower() != scene_label.lower():
                comparison.label_mismatches.append(f"{entity_id}: plan='{label}' scene='{scene_label}'")
            continue

        scene_obj = _match_by_label(scene.objects, entity.get('label'))
        if scene_obj:
            matched_scene_ids.add(scene_obj.id)
            continue

        comparison.missing_in_scene.append(entity_id)

    for obj in scene.objects:
        if obj.id not in plan_entities and obj.id not in matched_scene_ids:
            comparison.extra_scene_objects.append(obj.id)

    plan_relations = _extract_plan_relations(diagram_plan)
    for rel in plan_relations:
        src = rel.get('source_id') or rel.get('source')
        tgt = rel.get('target_id') or rel.get('target')
        if not src or not tgt:
            continue
        if src in comparison.missing_in_scene or tgt in comparison.missing_in_scene:
            comparison.relation_gaps.append(f"Missing relation {src}->{tgt}")

    total_expected = len(plan_entities) if plan_entities else 1
    penalty = (len(comparison.missing_in_scene) + len(comparison.label_mismatches) * 0.5) / total_expected
    comparison.score = max(0.0, 1.0 - penalty)
    return comparison


def _extract_plan_entities(diagram_plan: Any) -> Dict[str, Dict[str, Any]]:
    entities: List[Dict[str, Any]] = []
    if hasattr(diagram_plan, 'extracted_entities') and diagram_plan.extracted_entities:
        entities = diagram_plan.extracted_entities
    elif hasattr(diagram_plan, 'entities') and diagram_plan.entities:
        entities = diagram_plan.entities
    entity_map: Dict[str, Dict[str, Any]] = {}
    for entity in entities:
        entity_id = entity.get('id') or entity.get('name')
        if entity_id:
            entity_map[str(entity_id)] = entity
    return entity_map


def _extract_plan_relations(diagram_plan: Any) -> List[Dict[str, Any]]:
    if hasattr(diagram_plan, 'extracted_relations') and diagram_plan.extracted_relations:
        return list(diagram_plan.extracted_relations)
    if hasattr(diagram_plan, 'relationships') and diagram_plan.relationships:
        return list(diagram_plan.relationships)
    return []


def _match_by_label(objects: List[Any], label: Optional[str]):
    if not label:
        return None
    label_lower = label.lower()
    for obj in objects:
        obj_label = obj.properties.get('label') if obj.properties else None
        if obj_label and obj_label.lower() == label_lower:
            return obj
    return None
