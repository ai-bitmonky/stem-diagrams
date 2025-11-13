"""
Generate HTML trace report from JSON trace file
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def generate_html_trace(trace_json_path: str, output_html_path: str):
    """Generate HTML trace report from JSON trace file"""

    # Load trace JSON
    with open(trace_json_path, 'r') as f:
        trace = json.load(f)

    request_id = trace.get('request_id', 'N/A')
    timestamp = trace.get('timestamp', 'N/A')
    status = trace.get('status', 'unknown')
    total_duration = trace.get('total_duration_ms', 0)
    phases = trace.get('phases', [])

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pipeline Trace - {request_id}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}

        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}

        .summary-card .label {{
            font-size: 0.85em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .summary-card .value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}

        .summary-card.success .value {{
            color: #28a745;
        }}

        .summary-card.error .value {{
            color: #dc3545;
        }}

        .phases {{
            padding: 40px;
        }}

        .phase {{
            margin-bottom: 30px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .phase:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .phase-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .phase-header:hover {{
            background: linear-gradient(135deg, #5568d3 0%, #6941a0 100%);
        }}

        .phase-title {{
            font-size: 1.3em;
            font-weight: bold;
        }}

        .phase-duration {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}

        .phase-body {{
            padding: 20px;
            background: white;
        }}

        .phase-body.collapsed {{
            display: none;
        }}

        .phase-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }}

        .info-box {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }}

        .info-box h4 {{
            color: #667eea;
            margin-bottom: 10px;
            font-size: 0.9em;
            text-transform: uppercase;
        }}

        .info-box pre {{
            background: white;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 0.85em;
            line-height: 1.5;
        }}

        .timeline {{
            padding: 40px;
            background: #f8f9fa;
        }}

        .timeline h2 {{
            margin-bottom: 30px;
            color: #333;
        }}

        .timeline-bar {{
            height: 60px;
            background: #e9ecef;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
        }}

        .timeline-segment {{
            position: absolute;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 0.85em;
            font-weight: bold;
            transition: all 0.3s ease;
            cursor: pointer;
        }}

        .timeline-segment:hover {{
            filter: brightness(1.1);
            z-index: 10;
        }}

        .timeline-legend {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .legend-color {{
            width: 30px;
            height: 30px;
            border-radius: 4px;
        }}

        .legend-text {{
            font-size: 0.9em;
        }}

        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
        }}

        .status-success {{
            background: #d4edda;
            color: #155724;
        }}

        .status-error {{
            background: #f8d7da;
            color: #721c24;
        }}

        .footer {{
            padding: 20px 40px;
            background: #f8f9fa;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            .phase-info {{
                grid-template-columns: 1fr;
            }}

            .summary {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
    <script>
        function togglePhase(phaseId) {{
            const body = document.getElementById('phase-body-' + phaseId);
            body.classList.toggle('collapsed');
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Pipeline Execution Trace</h1>
            <div class="subtitle">Request ID: {request_id}</div>
            <div class="subtitle">{timestamp}</div>
        </div>

        <div class="summary">
            <div class="summary-card {'success' if status == 'success' else 'error'}">
                <div class="label">Status</div>
                <div class="value">{'✅ SUCCESS' if status == 'success' else '❌ ERROR'}</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Duration</div>
                <div class="value">{total_duration:.2f}ms</div>
            </div>
            <div class="summary-card">
                <div class="label">Phases Completed</div>
                <div class="value">{len(phases)}</div>
            </div>
            <div class="summary-card">
                <div class="label">Average Phase Duration</div>
                <div class="value">{(total_duration / len(phases) if phases else 0):.2f}ms</div>
            </div>
        </div>
"""

    # Add timeline visualization
    html += """
        <div class="timeline">
            <h2>⏱️ Execution Timeline</h2>
            <div class="timeline-bar">
"""

    colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140', '#30cfd0']
    cumulative_percent = 0

    for i, phase in enumerate(phases):
        duration = phase.get('duration_ms', 0)
        percent = (duration / total_duration * 100) if total_duration > 0 else 0
        color = colors[i % len(colors)]

        html += f"""
                <div class="timeline-segment" style="left: {cumulative_percent}%; width: {percent}%; background: {color};"
                     title="{phase.get('phase_name', 'Unknown')}: {duration:.2f}ms">
                    {phase.get('phase_name', 'Unknown')[:15]}{'...' if len(phase.get('phase_name', '')) > 15 else ''}
                </div>
"""
        cumulative_percent += percent

    html += """
            </div>
            <div class="timeline-legend">
"""

    for i, phase in enumerate(phases):
        color = colors[i % len(colors)]
        duration = phase.get('duration_ms', 0)
        percent = (duration / total_duration * 100) if total_duration > 0 else 0

        html += f"""
                <div class="legend-item">
                    <div class="legend-color" style="background: {color};"></div>
                    <div class="legend-text">{phase.get('phase_name', 'Unknown')}<br><small>{duration:.2f}ms ({percent:.1f}%)</small></div>
                </div>
"""

    html += """
            </div>
        </div>
"""

    # Add phases
    html += """
        <div class="phases">
            <h2>📋 Phase Details</h2>
"""

    for i, phase in enumerate(phases):
        phase_name = phase.get('phase_name', 'Unknown')
        description = phase.get('description', '')
        duration = phase.get('duration_ms', 0)
        status = phase.get('status', 'unknown')
        input_data = phase.get('input', {})
        output_data = phase.get('output', {})

        html += f"""
            <div class="phase">
                <div class="phase-header" onclick="togglePhase({i})">
                    <div>
                        <div class="phase-title">Phase {phase.get('phase_number', i)}: {phase_name}</div>
                        <div style="font-size: 0.9em; opacity: 0.9; margin-top: 5px;">{description}</div>
                    </div>
                    <div>
                        <span class="status-badge status-{status}">{status}</span>
                        <span class="phase-duration">{duration:.2f}ms</span>
                    </div>
                </div>
                <div class="phase-body" id="phase-body-{i}">
                    <div class="phase-info">
                        <div class="info-box">
                            <h4>📥 Input</h4>
                            <pre>{json.dumps(input_data, indent=2) if isinstance(input_data, (dict, list)) else str(input_data)[:500]}</pre>
                        </div>
                        <div class="info-box">
                            <h4>📤 Output</h4>
                            <pre>{json.dumps(output_data, indent=2)}</pre>
                        </div>
                    </div>
                </div>
            </div>
"""

    html += """
        </div>

        <div class="footer">
            Generated by Pipeline Logger • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""

    # Write HTML file
    with open(output_html_path, 'w') as f:
        f.write(html)

    print(f"✅ HTML trace generated: {output_html_path}")

if __name__ == "__main__":
    # Find latest trace JSON
    log_dir = Path("logs")
    if not log_dir.exists():
        print("❌ No logs directory found")
        sys.exit(1)

    trace_files = list(log_dir.glob("*_trace.json"))
    if not trace_files:
        print("❌ No trace files found")
        sys.exit(1)

    latest_trace = max(trace_files, key=lambda p: p.stat().st_mtime)
    output_html = latest_trace.with_suffix('.html')

    print(f"📊 Generating HTML trace from: {latest_trace}")
    generate_html_trace(str(latest_trace), str(output_html))
    print(f"📄 Open in browser: {output_html.absolute()}")
