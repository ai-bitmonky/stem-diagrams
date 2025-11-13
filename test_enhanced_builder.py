#!/usr/bin/env python3
"""
Test Enhanced Scene Builder
===========================

Quick test to verify the new detailed capacitor representation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.advanced_scene_builder import AdvancedSceneBuilder
from core.universal_svg_renderer import UniversalSVGRenderer

# Question 6 text
problem_text = """A parallel-plate capacitor has plates of area 0.12 m² and a separation of 1.2 cm.
A battery charges the plates to a potential difference of 120 V and is then disconnected.
A dielectric slab of thickness 4.0 mm and dielectric constant κ = 4.8 is then placed symmetrically
between the plates. What is the magnitude of the electric field in the dielectric after insertion?"""

print("=" * 80)
print("TESTING ENHANCED SCENE BUILDER")
print("=" * 80)
print(f"\nProblem: {problem_text[:100]}...")

# Mock NLP results (simplified)
nlp_results = {
    'domain': 'electronics',
    'entities': [],
    'relationships': [],
    'text': problem_text
}

# Build scene
print("\n[1] Building scene with enhanced builder...")
builder = AdvancedSceneBuilder()
scene = builder.build_capacitor_scene(nlp_results, problem_text)

print(f"✓ Scene created: {scene.title}")
print(f"  • Objects: {len(scene.objects)}")
print(f"  • Relationships: {len(scene.relationships)}")
print(f"  • Annotations: {len(scene.annotations)}")

print("\n[2] Object breakdown:")
object_types = {}
for obj in scene.objects:
    obj_type = str(obj.object_type)
    object_types[obj_type] = object_types.get(obj_type, 0) + 1
    if len(scene.objects) <= 20:  # Only print details if not too many
        print(f"  • {obj.id}: {obj.object_type} at ({obj.position.x:.0f}, {obj.position.y:.0f})")

print("\n[3] Object type summary:")
for obj_type, count in object_types.items():
    print(f"  • {obj_type}: {count}")

# Render to SVG
print("\n[4] Rendering to SVG...")
renderer = UniversalSVGRenderer()
svg_content = renderer.render(scene)
print(f"✓ Generated SVG ({len(svg_content):,} bytes)")

# Save
output_path = Path("test_data/enhanced_test_q6.svg")
output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(svg_content)
print(f"✓ Saved to: {output_path}")

print("\n" + "=" * 80)
print("✅ TEST COMPLETE")
print("=" * 80)
print(f"\nComparison:")
print(f"  Original: 2 objects (battery + capacitor)")
print(f"  Enhanced: {len(scene.objects)} objects")
print(f"  Improvement: {len(scene.objects) / 2:.1f}x more detail!")
