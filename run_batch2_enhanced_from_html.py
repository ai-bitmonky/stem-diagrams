"""
Run Enhanced Pipeline on All Batch 2 Questions from HTML File
==============================================================

This script extracts all 5 questions from batch_2_questions.html and
processes them through the Enhanced Pipeline with Phase 2+ features.

Author: Universal Diagram Generator Team
Date: November 5, 2025
"""

from enhanced_diagram_generator import EnhancedDiagramGenerator
import time
from pathlib import Path

# Extracted questions from batch_2_questions.html
BATCH_2_QUESTIONS = [
    {
        'id': 'question_6',
        'number': 6,
        'title': 'Parallel-Plate Capacitor with Dielectric',
        'problem': """A parallel-plate capacitor has plates of area 0.12 m² and a separation of 1.2 cm. A battery charges the plates to a potential difference of 120 V and is then disconnected. A dielectric slab of thickness 4.0 mm and dielectric constant κ = 4.8 is then placed symmetrically between the plates. What is the magnitude of the electric field in the dielectric after insertion?"""
    },
    {
        'id': 'question_7',
        'number': 7,
        'title': 'Series Capacitors Reconnected',
        'problem': """A potential difference of 300 V is applied to a series connection of two capacitors of capacitances C₁ = 2.00 μF and C₂ = 8.00 μF. The charged capacitors are then disconnected from the battery and from each other. They are then reconnected with plates of the same signs wired together (positive to positive, negative to negative). What is the charge on capacitor C₁?"""
    },
    {
        'id': 'question_8',
        'number': 8,
        'title': 'Multi-Region Dielectric Capacitor',
        'problem': """A parallel-plate capacitor of plate area A = 10.5 cm² and plate separation 2d = 7.12 mm is configured as follows: The left half is filled with dielectric κ₁ = 21.0. The right half is divided into two regions - top with κ₂ = 42.0 and bottom with κ₃ = 58.0. Calculate the total capacitance. [Left half: uniform κ₁; Right half: top quarter κ₂, bottom quarter κ₃]"""
    },
    {
        'id': 'question_9',
        'number': 9,
        'title': 'Variable Capacitor Circuit Analysis',
        'problem': """Capacitor 3 in the circuit is a variable capacitor (its capacitance C₃ can be varied). The electric potential V₁ across capacitor 1 approaches an asymptote of 10 V as C₃ → ∞. The horizontal scale is set by C₃ₛ = 12.0 μF. Circuit Configuration: C₁ is in series with the parallel combination of C₂ and C₃. Determine: (a) The electric potential V across the battery, (b) The capacitance C₁, (c) The capacitance C₂"""
    },
    {
        'id': 'question_10',
        'number': 10,
        'title': 'Safety Evaluation - Charged Liquid Container',
        'problem': """As a safety engineer, you must evaluate the practice of storing flammable conducting liquids in nonconducting containers. The company uses a squat, cylindrical plastic container of radius r = 0.20 m and filling it to height h = 10 cm. Given: Container radius r = 0.20 m, Liquid height h = 0.10 m, Surface charge density σ = 2.0 μC/m², Capacitance of liquid's central portion C = 35 pF, Minimum spark energy to ignite E_min = 10 mJ. Determine: (a) How much negative charge is induced in the center of the liquid's bulk? (b) What is the potential energy associated with the negative charge in that effective capacitor? (c) Can a spark from the central portion of the liquid ignite the liquid if the spark energy equals the stored potential energy?"""
    }
]


def main():
    print("=" * 80)
    print("ENHANCED PIPELINE - BATCH 2 QUESTIONS FROM HTML")
    print("=" * 80)
    print()
    print("Processing all 5 questions from batch_2_questions.html")
    print("Using Phase 2+ Enhanced Pipeline with:")
    print("  - Advanced Scene Builder with physics rules")
    print("  - Enhanced NLP with dual extraction")
    print("  - Physics validation")
    print()

    # Initialize enhanced generator
    output_dir = "output/batch2_html_enhanced"
    generator = EnhancedDiagramGenerator(output_dir=output_dir)

    results = []
    total_start = time.time()

    # Process each question
    for question in BATCH_2_QUESTIONS:
        print(f"\n{'='*80}")
        print(f"Question {question['number']}: {question['title']}")
        print(f"{'='*80}")

        start = time.time()
        result = generator.generate(
            question['problem'],
            f"q{question['number']}_{question['id']}",
            save_files=True
        )
        elapsed = time.time() - start

        results.append({
            'question': question,
            'result': result,
            'time': elapsed
        })

        if result['success']:
            print(f"\n✅ Question {question['number']} - SUCCESS")
            print(f"   Domain: {result['metadata']['domain']}")
            print(f"   Entities: {result['nlp_results']['metadata']['num_entities']}")
            print(f"   NLP Relationships: {result['nlp_results']['metadata']['num_relationships']}")
            print(f"   Objects: {result['metadata']['num_objects']}")
            print(f"   Scene Relationships: {result['metadata']['num_relationships']}")
            print(f"   Annotations: {result['metadata']['num_annotations']}")
            print(f"   Processing time: {elapsed:.3f}s")

            if result['metadata']['validation_warnings']:
                print(f"   ⚠️  Validation warnings: {len(result['metadata']['validation_warnings'])}")
                for warning in result['metadata']['validation_warnings']:
                    print(f"      - {warning}")
        else:
            print(f"\n❌ Question {question['number']} - FAILED")
            print(f"   Error: {result['error']}")

    total_time = time.time() - total_start

    # Summary
    print("\n" + "=" * 80)
    print("ENHANCED PIPELINE SUMMARY - BATCH 2 HTML")
    print("=" * 80)

    success_count = sum(1 for r in results if r['result']['success'])
    success_rate = (success_count / len(results)) * 100

    print(f"\n📊 Overall Statistics:")
    print(f"   Total questions: {len(results)}")
    print(f"   Successful: {success_count}")
    print(f"   Failed: {len(results) - success_count}")
    print(f"   Success rate: {success_rate:.1f}%")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Average time: {total_time/len(results):.3f}s per question")

    if success_count > 0:
        # Detailed statistics
        total_entities = sum(r['result']['nlp_results']['metadata']['num_entities']
                            for r in results if r['result']['success'])
        total_nlp_relationships = sum(r['result']['nlp_results']['metadata']['num_relationships']
                                     for r in results if r['result']['success'])
        total_objects = sum(r['result']['metadata']['num_objects']
                           for r in results if r['result']['success'])
        total_scene_relationships = sum(r['result']['metadata']['num_relationships']
                                        for r in results if r['result']['success'])
        total_annotations = sum(r['result']['metadata']['num_annotations']
                               for r in results if r['result']['success'])

        print(f"\n📈 Enhanced Pipeline Features:")
        print(f"   Total entities extracted: {total_entities}")
        print(f"   Avg entities per question: {total_entities/success_count:.1f}")
        print(f"   Total NLP relationships: {total_nlp_relationships}")
        print(f"   Avg NLP relationships per question: {total_nlp_relationships/success_count:.1f}")
        print(f"   Total scene objects: {total_objects}")
        print(f"   Avg objects per question: {total_objects/success_count:.1f}")
        print(f"   Total scene relationships: {total_scene_relationships}")
        print(f"   Total annotations: {total_annotations}")

    print(f"\n📁 Output:")
    print(f"   Directory: {output_dir}")
    print(f"   Files generated: {success_count * 3} files")
    print(f"   - {success_count} SVG diagrams")
    print(f"   - {success_count} Scene JSON files")
    print(f"   - {success_count} NLP JSON files")

    # Generate HTML gallery
    print(f"\n📄 Generating HTML gallery...")
    generate_html_gallery(results, total_time, success_rate, output_dir)

    print("\n" + "=" * 80)
    print("✅ Enhanced pipeline processing complete!")
    print("=" * 80)
    print(f"\nView results: {output_dir}/BATCH2_HTML_ENHANCED_GALLERY.html")


def generate_html_gallery(results, total_time, success_rate, output_dir):
    """Generate HTML gallery for all results"""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Batch 2: Enhanced Pipeline from HTML</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .question-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(700px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        .question-card {{
            border: 2px solid #eee;
            border-radius: 10px;
            padding: 20px;
            background: #f9f9f9;
        }}
        .question-card h3 {{
            color: #667eea;
            margin-top: 0;
        }}
        .diagram-preview {{
            background: white;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            text-align: center;
        }}
        .diagram-preview svg {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
        }}
        .stats-table {{
            margin: 15px 0;
            font-size: 14px;
        }}
        .stats-table tr {{
            line-height: 1.8;
        }}
        .stats-table td:first-child {{
            font-weight: bold;
            color: #667eea;
            padding-right: 10px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin: 2px;
        }}
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        .badge-enhanced {{
            background: #e8daef;
            color: #6c3483;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Batch 2: Enhanced Pipeline Results</h1>
        <p class="subtitle">All 5 questions processed from batch_2_questions.html using Phase 2+ Enhanced Pipeline</p>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value">{success_rate:.1f}%</div>
                <div class="stat-label">{sum(1 for r in results if r['result']['success'])}/5 questions</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Time</div>
                <div class="stat-value">{total_time:.3f}s</div>
                <div class="stat-label">{total_time/len(results):.3f}s avg</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Entities</div>
                <div class="stat-value">{sum(r['result']['nlp_results']['metadata']['num_entities'] for r in results if r['result']['success'])}</div>
                <div class="stat-label">Enhanced extraction</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Objects</div>
                <div class="stat-value">{sum(r['result']['metadata']['num_objects'] for r in results if r['result']['success'])}</div>
                <div class="stat-label">Scene components</div>
            </div>
        </div>

        <h2>Generated Diagrams</h2>
        <div class="question-grid">
"""

    for r in results:
        q = r['question']
        result = r['result']

        if result['success']:
            html += f"""
            <div class="question-card">
                <h3>Question {q['number']}: {q['title']}</h3>
                <div>
                    <span class="badge badge-success">SUCCESS</span>
                    <span class="badge badge-enhanced">Phase 2+</span>
                </div>

                <table class="stats-table">
                    <tr><td>Entities:</td><td>{result['nlp_results']['metadata']['num_entities']}</td></tr>
                    <tr><td>NLP Relationships:</td><td>{result['nlp_results']['metadata']['num_relationships']}</td></tr>
                    <tr><td>Objects:</td><td>{result['metadata']['num_objects']}</td></tr>
                    <tr><td>Scene Relationships:</td><td>{result['metadata']['num_relationships']}</td></tr>
                    <tr><td>Annotations:</td><td>{result['metadata']['num_annotations']}</td></tr>
                    <tr><td>Processing Time:</td><td>{r['time']:.3f}s</td></tr>
                </table>

                <div class="diagram-preview">
                    {result['svg']}
                </div>

                <p style="font-size: 12px; color: #666; margin-top: 10px;">
                    <strong>Files:</strong>
                    q{q['number']}_{q['id']}.svg,
                    q{q['number']}_{q['id']}_scene.json,
                    q{q['number']}_{q['id']}_nlp.json
                </p>
            </div>
"""
        else:
            html += f"""
            <div class="question-card" style="background: #fff3e0;">
                <h3>Question {q['number']}: {q['title']}</h3>
                <p style="color: #e65100;"><strong>Error:</strong> {result['error']}</p>
            </div>
"""

    html += """
        </div>

        <div style="margin-top: 30px; padding: 20px; background: #e8f5e9; border-radius: 10px;">
            <h3 style="color: #2e7d32; margin-top: 0;">✅ Phase 2+ Features Used</h3>
            <ul>
                <li><strong>Advanced Scene Builder:</strong> Physics-aware component positioning and validation</li>
                <li><strong>Enhanced NLP:</strong> Dual extraction (spaCy NER + Enhanced Regex)</li>
                <li><strong>High Confidence:</strong> 0.95 confidence for scientific measurements</li>
                <li><strong>Rich Relationships:</strong> Proximity-based and pattern-based detection</li>
                <li><strong>Intelligent Layout:</strong> Optimal component spacing using physics engine</li>
            </ul>
        </div>

        <p style="text-align: center; margin-top: 30px; color: #666;">
            Generated on November 5, 2025 | Enhanced Pipeline with Phase 2+ Features
        </p>
    </div>
</body>
</html>
"""

    output_path = Path(output_dir) / "BATCH2_HTML_ENHANCED_GALLERY.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"   ✅ Gallery saved: {output_path}")


if __name__ == "__main__":
    main()
