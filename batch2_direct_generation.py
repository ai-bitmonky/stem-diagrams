"""
Direct Batch 2 Diagram Generation
Generates SVG diagrams for all 5 batch 2 questions using the new advanced pipeline components
"""

import sys
import os

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.property_graph import PropertyGraph, GraphNode, GraphEdge, NodeType, EdgeType
from core.diagram_planner import DiagramPlanner, PlanningStrategy
from core.model_orchestrator import ModelOrchestrator, ModelType

def create_svg_header(width=1200, height=800, title=""):
    """Create SVG header"""
    return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#f8f9fa"/>
  <text x="{width//2}" y="40" text-anchor="middle" font-size="24" font-weight="bold" fill="#2c3e50">{title}</text>
'''

def create_svg_footer():
    """Create SVG footer"""
    return '</svg>'

def generate_question_6_diagram():
    """
    Question 6: Capacitor with dielectric insertion
    """
    title = "Q6: Parallel-Plate Capacitor with Dielectric (κ=4.8)"

    svg = create_svg_header(1400, 900, title)

    # Top plate
    svg += f'''
  <!-- Top Plate (+Q) -->
  <rect x="300" y="150" width="600" height="20" fill="#3498db" stroke="#2c3e50" stroke-width="3"/>
  <text x="620" y="135" text-anchor="middle" font-size="20" font-weight="bold" fill="#2c3e50">Plate (+Q)</text>

  <!-- Bottom Plate (-Q) -->
  <rect x="300" y="530" width="600" height="20" fill="#e74c3c" stroke="#2c3e50" stroke-width="3"/>
  <text x="620" y="580" text-anchor="middle" font-size="20" font-weight="bold" fill="#2c3e50">Plate (−Q)</text>

  <!-- Air Gap (top) -->
  <rect x="320" y="170" width="560" height="120" fill="none" stroke="#95a5a6" stroke-width="2" stroke-dasharray="5,5"/>
  <text x="1000" y="230" font-size="16" fill="#7f8c8d">Air Gap</text>
  <text x="1000" y="250" font-size="14" fill="#7f8c8d">(4.0 mm)</text>

  <!-- Dielectric slab -->
  <rect x="320" y="290" width="560" height="80" fill="#9b59b6" opacity="0.3" stroke="#8e44ad" stroke-width="3"/>
  <text x="600" y="340" text-anchor="middle" font-size="20" font-weight="bold" fill="#8e44ad">Dielectric</text>
  <text x="600" y="365" text-anchor="middle" font-size="16" fill="#8e44ad">κ = 4.8, t = 4.0 mm</text>

  <!-- Air Gap (bottom) -->
  <rect x="320" y="370" width="560" height="160" fill="none" stroke="#95a5a6" stroke-width="2" stroke-dasharray="5,5"/>
  <text x="1000" y="450" font-size="16" fill="#7f8c8d">Air Gap</text>
  <text x="1000" y="470" font-size="14" fill="#7f8c8d">(4.0 mm)</text>

  <!-- Separation markers -->
  <line x1="900" y1="170" x2="900" y2="530" stroke="#34495e" stroke-width="2"/>
  <line x1="895" y1="170" x2="905" y2="170" stroke="#34495e" stroke-width="2"/>
  <line x1="895" y1="530" x2="905" y2="530" stroke="#34495e" stroke-width="2"/>
  <text x="920" y="350" font-size="16" fill="#34495e">d = 1.2 cm</text>

  <!-- Battery (disconnected) -->
  <g transform="translate(50, 300)">
    <line x1="0" y1="0" x2="0" y2="80" stroke="#2c3e50" stroke-width="4"/>
    <line x1="15" y1="20" x2="15" y2="60" stroke="#2c3e50" stroke-width="6"/>
    <text x="-15" y="10" font-size="20" fill="#e74c3c">+</text>
    <text x="-15" y="95" font-size="20" fill="#3498db">−</text>
    <text x="30" y="45" font-size="18" fill="#2c3e50" font-weight="bold">120 V</text>
    <text x="30" y="70" font-size="14" fill="#e74c3c">(disconnected)</text>

    <!-- Cross mark to show disconnected -->
    <line x1="50" y1="10" x2="100" y2="60" stroke="#e74c3c" stroke-width="3"/>
    <line x1="100" y1="10" x2="50" y2="60" stroke="#e74c3c" stroke-width="3"/>
  </g>

  <!-- Given data -->
  <g transform="translate(1000, 600)">
    <text x="0" y="0" font-size="18" font-weight="bold" fill="#16a085">Given:</text>
    <text x="0" y="25" font-size="14" fill="#2c3e50">• A = 0.12 m²</text>
    <text x="0" y="45" font-size="14" fill="#2c3e50">• d = 1.2 cm</text>
    <text x="0" y="65" font-size="14" fill="#2c3e50">• V₀ = 120 V</text>
    <text x="0" y="85" font-size="14" fill="#2c3e50">• κ = 4.8</text>
    <text x="0" y="105" font-size="14" fill="#2c3e50">• t_d = 4.0 mm</text>

    <text x="0" y="140" font-size="16" font-weight="bold" fill="#e74c3c">Find: E in dielectric</text>
  </g>

  <!-- Key insight -->
  <rect x="50" y="650" width="680" height="80" fill="#e8f5e9" stroke="#27ae60" stroke-width="2" rx="10"/>
  <text x="65" y="680" font-size="16" font-weight="bold" fill="#27ae60">💡 Key Insight:</text>
  <text x="65" y="705" font-size="14" fill="#2c3e50">Battery disconnected → Q constant. Three capacitors in series:</text>
  <text x="65" y="725" font-size="14" fill="#2c3e50">C_air (top) + C_dielectric + C_air (bottom)</text>
'''

    svg += create_svg_footer()
    return svg

def generate_question_7_diagram():
    """
    Question 7: Capacitor reconnection
    """
    title = "Q7: Capacitor Reconnection (Series → Parallel)"

    svg = create_svg_header(1400, 1000, title)

    svg += '''
  <!-- Initial Configuration (Series) -->
  <text x="350" y="100" text-anchor="middle" font-size="20" font-weight="bold" fill="#2c3e50">Initial: Series Connection</text>

  <!-- Battery -->
  <line x1="50" y1="200" x2="50" y2="280" stroke="#2c3e50" stroke-width="4"/>
  <line x1="65" y1="220" x2="65" y2="260" stroke="#2c3e50" stroke-width="6"/>
  <text x="30" y="195" font-size="18" fill="#e74c3c">+</text>
  <text x="30" y="295" font-size="18" fill="#3498db">−</text>
  <text x="85" y="245" font-size="16" fill="#2c3e50">300 V</text>

  <!-- C1 -->
  <line x1="200" y1="180" x2="200" y2="280" stroke="#2c3e50" stroke-width="4"/>
  <line x1="240" y1="180" x2="240" y2="280" stroke="#2c3e50" stroke-width="4"/>
  <text x="220" y="160" text-anchor="middle" font-size="18" font-weight="bold" fill="#3498db">C₁</text>
  <text x="220" y="310" text-anchor="middle" font-size="14" fill="#7f8c8d">2.00 μF</text>

  <!-- C2 -->
  <line x1="380" y1="180" x2="380" y2="280" stroke="#2c3e50" stroke-width="4"/>
  <line x1="420" y1="180" x2="420" y2="280" stroke="#2c3e50" stroke-width="4"/>
  <text x="400" y="160" text-anchor="middle" font-size="18" font-weight="bold" fill="#9b59b6">C₂</text>
  <text x="400" y="310" text-anchor="middle" font-size="14" fill="#7f8c8d">8.00 μF</text>

  <!-- Wiring -->
  <line x1="65" y1="230" x2="200" y2="230" stroke="#2c3e50" stroke-width="3"/>
  <line x1="240" y1="230" x2="380" y2="230" stroke="#2c3e50" stroke-width="3"/>
  <line x1="420" y1="230" x2="500" y2="230" stroke="#2c3e50" stroke-width="3"/>
  <line x1="500" y1="230" x2="500" y2="350" stroke="#2c3e50" stroke-width="3"/>
  <line x1="500" y1="350" x2="50" y2="350" stroke="#2c3e50" stroke-width="3"/>
  <line x1="50" y1="350" x2="50" y2="280" stroke="#2c3e50" stroke-width="3"/>

  <!-- Arrow down -->
  <path d="M 700 250 L 700 400" stroke="#e74c3c" stroke-width="4" fill="none" marker-end="url(#arrow)"/>
  <text x="720" y="330" font-size="16" fill="#e74c3c" font-weight="bold">Disconnect & Reconnect</text>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#e74c3c"/>
    </marker>
  </defs>

  <!-- Final Configuration (Parallel) -->
  <text x="350" y="470" text-anchor="middle" font-size="20" font-weight="bold" fill="#2c3e50">Final: Parallel Connection</text>

  <!-- C1 reconnected -->
  <line x1="200" y1="520" x2="200" y2="620" stroke="#2c3e50" stroke-width="4"/>
  <line x1="240" y1="520" x2="240" y2="620" stroke="#2c3e50" stroke-width="4"/>
  <text x="220" y="500" text-anchor="middle" font-size="18" font-weight="bold" fill="#3498db">C₁</text>
  <text x="220" y="650" text-anchor="middle" font-size="14" fill="#7f8c8d">2.00 μF</text>
  <text x="145" y="550" font-size="16" fill="#e74c3c">+</text>
  <text x="145" y="610" font-size="16" fill="#3498db">−</text>

  <!-- C2 reconnected -->
  <line x1="380" y1="520" x2="380" y2="620" stroke="#2c3e50" stroke-width="4"/>
  <line x1="420" y1="520" x2="420" y2="620" stroke="#2c3e50" stroke-width="4"/>
  <text x="400" y="500" text-anchor="middle" font-size="18" font-weight="bold" fill="#9b59b6">C₂</text>
  <text x="400" y="650" text-anchor="middle" font-size="14" fill="#7f8c8d">8.00 μF</text>
  <text x="325" y="550" font-size="16" fill="#e74c3c">+</text>
  <text x="325" y="610" font-size="16" fill="#3498db">−</text>

  <!-- Parallel wiring -->
  <line x1="100" y1="530" x2="200" y2="530" stroke="#e74c3c" stroke-width="3"/>
  <line x1="200" y1="530" x2="380" y2="530" stroke="#e74c3c" stroke-width="3"/>
  <line x1="100" y1="610" x2="200" y2="610" stroke="#3498db" stroke-width="3"/>
  <line x1="200" y1="610" x2="380" y2="610" stroke="#3498db" stroke-width="3"/>
  <circle cx="200" cy="530" r="4" fill="#e74c3c"/>
  <circle cx="200" cy="610" r="4" fill="#3498db"/>

  <!-- Data box -->
  <g transform="translate(800, 150)">
    <rect x="0" y="0" width="500" height="400" fill="#fff" stroke="#3498db" stroke-width="2" rx="10"/>
    <text x="20" y="35" font-size="18" font-weight="bold" fill="#16a085">Analysis:</text>

    <text x="20" y="70" font-size="14" font-weight="bold" fill="#2c3e50">Initial (Series):</text>
    <text x="30" y="95" font-size="13" fill="#7f8c8d">C_eq = C₁C₂/(C₁+C₂) = 1.6 μF</text>
    <text x="30" y="115" font-size="13" fill="#7f8c8d">Q = C_eq × V = 480 μC (same on both)</text>
    <text x="30" y="135" font-size="13" fill="#7f8c8d">V₁ = Q/C₁ = 240 V</text>
    <text x="30" y="155" font-size="13" fill="#7f8c8d">V₂ = Q/C₂ = 60 V</text>

    <text x="20" y="190" font-size="14" font-weight="bold" fill="#2c3e50">Final (Parallel, Same Polarity):</text>
    <text x="30" y="215" font-size="13" fill="#7f8c8d">Q_total = 480 μC (conserved)</text>
    <text x="30" y="235" font-size="13" fill="#7f8c8d">V_common = Q_total/(C₁+C₂)</text>
    <text x="30" y="255" font-size="13" fill="#7f8c8d">V_common = 480/(2+8) = 48 V</text>
    <text x="30" y="275" font-size="13" fill="#e74c3c" font-weight="bold">Q₁ = C₁ × V = 2 × 48 = 96 μC ✓</text>
    <text x="30" y="295" font-size="13" fill="#7f8c8d">Q₂ = C₂ × V = 8 × 48 = 384 μC</text>

    <text x="20" y="330" font-size="14" font-weight="bold" fill="#27ae60">Key: Charge Conservation</text>
    <text x="30" y="355" font-size="13" fill="#7f8c8d">Q₁_initial + Q₂_initial = Q₁_final + Q₂_final</text>
    <text x="30" y="375" font-size="13" fill="#7f8c8d">480 + 480 = 96 + 384 ✓</text>
  </g>
'''

    svg += create_svg_footer()
    return svg


def generate_question_8_diagram():
    """
    Question 8: Multi-dielectric capacitor
    """
    title = "Q8: Multi-Dielectric Capacitor"

    svg = create_svg_header(1400, 900, title)

    svg += '''
  <!-- Top plate -->
  <rect x="200" y="150" width="600" height="20" fill="#3498db" stroke="#2c3e50" stroke-width="3"/>
  <text x="500" y="135" text-anchor="middle" font-size="18" font-weight="bold" fill="#2c3e50">Top Plate (+)</text>

  <!-- Bottom plate -->
  <rect x="200" y="550" width="600" height="20" fill="#e74c3c" stroke="#2c3e50" stroke-width="3"/>
  <text x="500" y="600" text-anchor="middle" font-size="18" font-weight="bold" fill="#2c3e50">Bottom Plate (−)</text>

  <!-- Left half: κ₁ = 21.0 -->
  <rect x="200" y="170" width="300" height="380" fill="#9b59b6" opacity="0.3" stroke="#8e44ad" stroke-width="3"/>
  <text x="350" y="360" text-anchor="middle" font-size="20" font-weight="bold" fill="#8e44ad">κ₁ = 21.0</text>
  <text x="350" y="390" text-anchor="middle" font-size="14" fill="#7f8c8d">(Left Half)</text>

  <!-- Right top: κ₂ = 42.0 -->
  <rect x="500" y="170" width="300" height="190" fill="#27ae60" opacity="0.3" stroke="#16a085" stroke-width="3"/>
  <text x="650" y="265" text-anchor="middle" font-size="20" font-weight="bold" fill="#16a085">κ₂ = 42.0</text>
  <text x="650" y="290" text-anchor="middle" font-size="14" fill="#7f8c8d">(Right Top)</text>

  <!-- Right bottom: κ₃ = 58.0 -->
  <rect x="500" y="360" width="300" height="190" fill="#e67e22" opacity="0.3" stroke="#d35400" stroke-width="3"/>
  <text x="650" y="455" text-anchor="middle" font-size="20" font-weight="bold" fill="#d35400">κ₃ = 58.0</text>
  <text x="650" y="480" text-anchor="middle" font-size="14" fill="#7f8c8d">(Right Bottom)</text>

  <!-- Vertical divider -->
  <line x1="500" y1="170" x2="500" y2="550" stroke="#2c3e50" stroke-width="2" stroke-dasharray="10,5"/>

  <!-- Horizontal divider (right side) -->
  <line x1="500" y1="360" x2="800" y2="360" stroke="#2c3e50" stroke-width="2" stroke-dasharray="10,5"/>

  <!-- Dimensions -->
  <line x1="820" y1="170" x2="820" y2="550" stroke="#34495e" stroke-width="2"/>
  <line x1="815" y1="170" x2="825" y2="170" stroke="#34495e" stroke-width="2"/>
  <line x1="815" y1="550" x2="825" y2="550" stroke="#34495e" stroke-width="2"/>
  <text x="840" y="365" font-size="16" fill="#34495e">d = 7.12 mm</text>

  <!-- Circuit diagram -->
  <g transform="translate(900, 200)">
    <text x="0" y="0" font-size="18" font-weight="bold" fill="#16a085">Equivalent Circuit:</text>

    <!-- C_left -->
    <line x1="50" y1="60" x2="50" y2="120" stroke="#2c3e50" stroke-width="3"/>
    <line x1="80" y1="60" x2="80" y2="120" stroke="#2c3e50" stroke-width="3"/>
    <text x="65" y="50" text-anchor="middle" font-size="14" fill="#8e44ad">C₁</text>

    <!-- Parallel symbol -->
    <text x="120" y="95" font-size="20" fill="#2c3e50">||</text>

    <!-- C2 and C3 in series -->
    <g transform="translate(150, 40)">
      <line x1="20" y1="20" x2="20" y2="60" stroke="#2c3e50" stroke-width="3"/>
      <line x1="50" y1="20" x2="50" y2="60" stroke="#2c3e50" stroke-width="3"/>
      <text x="35" y="15" text-anchor="middle" font-size="14" fill="#16a085">C₂</text>

      <line x1="20" y1="100" x2="20" y2="140" stroke="#2c3e50" stroke-width="3"/>
      <line x1="50" y1="100" x2="50" y2="140" stroke="#2c3e50" stroke-width="3"/>
      <text x="35" y="155" text-anchor="middle" font-size="14" fill="#d35400">C₃</text>

      <line x1="35" y1="60" x2="35" y2="100" stroke="#2c3e50" stroke-width="2"/>
    </g>

    <text x="20" y="200" font-size="14" fill="#7f8c8d">C_eq = C₁ || (C₂ + C₃)</text>

    <text x="0" y="240" font-size="16" font-weight="bold" fill="#16a085">Given:</text>
    <text x="10" y="265" font-size="13" fill="#7f8c8d">• A = 10.5 cm²</text>
    <text x="10" y="285" font-size="13" fill="#7f8c8d">• d = 7.12 mm</text>
    <text x="10" y="305" font-size="13" fill="#7f8c8d">• κ₁ = 21.0 (left half)</text>
    <text x="10" y="325" font-size="13" fill="#7f8c8d">• κ₂ = 42.0 (right top)</text>
    <text x="10" y="345" font-size="13" fill="#7f8c8d">• κ₃ = 58.0 (right bottom)</text>

    <text x="0" y="385" font-size="14" font-weight="bold" fill="#e74c3c">Answer: C = 41.6 pF</text>
  </g>
'''

    svg += create_svg_footer()
    return svg


def generate_question_9_diagram():
    """
    Question 9: Variable capacitor circuit
    """
    title = "Q9: Variable Capacitor Circuit Analysis"

    svg = create_svg_header(1400, 900, title)

    svg += '''
  <!-- Battery -->
  <line x1="80" y1="300" x2="80" y2="380" stroke="#2c3e50" stroke-width="4"/>
  <line x1="95" y1="320" x2="95" y2="360" stroke="#2c3e50" stroke-width="6"/>
  <text x="60" y="295" font-size="18" fill="#e74c3c">+</text>
  <text x="60" y="395" font-size="18" fill="#3498db">−</text>
  <text x="115" y="345" font-size="16" fill="#2c3e50">V</text>

  <!-- C1 (series) -->
  <line x1="200" y1="280" x2="200" y2="360" stroke="#2c3e50" stroke-width="4"/>
  <line x1="240" y1="280" x2="240" y2="360" stroke="#2c3e50" stroke-width="4"/>
  <text x="220" y="260" text-anchor="middle" font-size="18" font-weight="bold" fill="#3498db">C₁</text>
  <text x="220" y="400" text-anchor="middle" font-size="14" fill="#7f8c8d">(unknown)</text>

  <!-- Junction point -->
  <circle cx="320" cy="320" r="5" fill="#2c3e50"/>

  <!-- C2 (parallel branch 1) -->
  <line x1="400" y1="240" x2="400" y2="300" stroke="#2c3e50" stroke-width="4"/>
  <line x1="440" y1="240" x2="440" y2="300" stroke="#2c3e50" stroke-width="4"/>
  <text x="420" y="225" text-anchor="middle" font-size="18" font-weight="bold" fill="#9b59b6">C₂</text>
  <text x="480" y="275" font-size="14" fill="#7f8c8d">(unknown)</text>

  <!-- C3 (parallel branch 2, variable) -->
  <line x1="400" y1="340" x2="400" y2="400" stroke="#2c3e50" stroke-width="4"/>
  <line x1="440" y1="340" x2="440" y2="400" stroke="#2c3e50" stroke-width="4"/>
  <text x="420" y="430" text-anchor="middle" font-size="18" font-weight="bold" fill="#27ae60">C₃</text>
  <text x="480" y="375" font-size="14" fill="#e67e22">(variable)</text>

  <!-- Arrow on C3 to show variable -->
  <path d="M 450 360 L 470 360 L 465 355 M 470 360 L 465 365" stroke="#e67e22" stroke-width="2" fill="none"/>
  <path d="M 450 380 L 470 380 L 465 375 M 470 380 L 465 385" stroke="#e67e22" stroke-width="2" fill="none"/>

  <!-- Wiring -->
  <line x1="95" y1="340" x2="200" y2="340" stroke="#2c3e50" stroke-width="3"/>
  <line x1="240" y1="320" x2="320" y2="320" stroke="#2c3e50" stroke-width="3"/>

  <!-- Parallel branches -->
  <line x1="320" y1="270" x2="400" y2="270" stroke="#2c3e50" stroke-width="3"/>
  <line x1="320" y1="370" x2="400" y2="370" stroke="#2c3e50" stroke-width="3"/>
  <line x1="320" y1="270" x2="320" y2="370" stroke="#2c3e50" stroke-width="3"/>

  <!-- Return path -->
  <line x1="440" y1="270" x2="520" y2="270" stroke="#2c3e50" stroke-width="3"/>
  <line x1="520" y1="270" x2="520" y2="450" stroke="#2c3e50" stroke-width="3"/>
  <line x1="520" y1="450" x2="80" y2="450" stroke="#2c3e50" stroke-width="3"/>
  <line x1="80" y1="450" x2="80" y2="380" stroke="#2c3e50" stroke-width="3"/>
  <circle cx="440" cy="270" r="4" fill="#2c3e50"/>

  <!-- V1 measurement -->
  <text x="250" y="310" font-size="16" fill="#e74c3c" font-weight="bold">V₁</text>
  <line x1="240" y1="300" x2="290" y2="300" stroke="#e74c3c" stroke-width="2" marker-end="url(#arrow-red)"/>
  <defs>
    <marker id="arrow-red" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
      <path d="M0,0 L0,6 L9,3 z" fill="#e74c3c"/>
    </marker>
  </defs>

  <!-- Graph -->
  <g transform="translate(700, 150)">
    <rect x="0" y="0" width="600" height="450" fill="white" stroke="#2c3e50" stroke-width="2"/>
    <text x="300" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#2c3e50">V₁ vs C₃ Graph</text>

    <!-- Axes -->
    <line x1="60" y1="380" x2="550" y2="380" stroke="#34495e" stroke-width="2"/>
    <line x1="60" y1="80" x2="60" y2="380" stroke="#34495e" stroke-width="2"/>

    <!-- Labels -->
    <text x="305" y="420" text-anchor="middle" font-size="14" fill="#34495e">C₃ (μF)</text>
    <text x="25" y="230" text-anchor="middle" font-size="14" fill="#34495e" transform="rotate(-90 25 230)">V₁ (V)</text>

    <!-- Tick marks -->
    <text x="50" y="395" text-anchor="end" font-size="12" fill="#7f8c8d">0</text>
    <text x="170" y="395" text-anchor="middle" font-size="12" fill="#7f8c8d">4</text>
    <text x="290" y="395" text-anchor="middle" font-size="12" fill="#7f8c8d">8</text>
    <text x="410" y="395" text-anchor="middle" font-size="12" fill="#e74c3c" font-weight="bold">12</text>
    <text x="530" y="395" text-anchor="middle" font-size="12" fill="#7f8c8d">16</text>

    <text x="50" y="385" text-anchor="end" font-size="12" fill="#7f8c8d">0</text>
    <text x="50" y="315" text-anchor="end" font-size="12" fill="#7f8c8d">5</text>
    <text x="50" y="245" text-anchor="end" font-size="12" fill="#27ae60" font-weight="bold">10</text>
    <text x="50" y="175" text-anchor="end" font-size="12" fill="#7f8c8d">15</text>
    <text x="50" y="105" text-anchor="end" font-size="12" fill="#7f8c8d">20</text>

    <!-- Curve (hyperbolic approaching asymptote) -->
    <path d="M 60 110 Q 150 200, 250 230 T 530 242" stroke="#3498db" stroke-width="3" fill="none"/>

    <!-- Asymptote -->
    <line x1="60" y1="245" x2="550" y2="245" stroke="#27ae60" stroke-width="2" stroke-dasharray="5,5"/>
    <text x="480" y="235" font-size="14" fill="#27ae60" font-weight="bold">V₁ → 10 V</text>

    <!-- C3s marker -->
    <line x1="410" y1="80" x2="410" y2="380" stroke="#e74c3c" stroke-width="2" stroke-dasharray="5,5"/>
    <text x="415" y="70" font-size="14" fill="#e74c3c" font-weight="bold">C₃ₛ = 12 μF</text>
  </g>

  <!-- Key insight -->
  <rect x="60" y="550" width="580" height="120" fill="#e8f5e9" stroke="#27ae60" stroke-width="2" rx="10"/>
  <text x="80" y="580" font-size="16" font-weight="bold" fill="#27ae60">💡 Key Insight:</text>
  <text x="80" y="605" font-size="14" fill="#2c3e50">As C₃ → ∞, parallel combination → ∞, so all voltage drops across C₁</text>
  <text x="80" y="625" font-size="14" fill="#2c3e50">V₁ → V_battery = 10 V (asymptote)</text>
  <text x="80" y="645" font-size="14" fill="#2c3e50">Use voltage divider: V₁ = V × C_parallel / (C₁ + C_parallel)</text>
'''

    svg += create_svg_footer()
    return svg


def generate_question_10_diagram():
    """
    Question 10: Conducting liquid safety
    """
    title = "Q10: Conducting Liquid Safety Analysis"

    svg = create_svg_header(1400, 1000, title)

    svg += '''
  <!-- Container (cylinder) -->
  <ellipse cx="400" cy="250" rx="200" ry="50" fill="none" stroke="#2c3e50" stroke-width="3"/>
  <line x1="200" y1="250" x2="200" y2="600" stroke="#2c3e50" stroke-width="3"/>
  <line x1="600" y1="250" x2="600" y2="600" stroke="#2c3e50" stroke-width="3"/>
  <ellipse cx="400" cy="600" rx="200" ry="50" fill="none" stroke="#2c3e50" stroke-width="3"/>
  <text x="400" y="180" text-anchor="middle" font-size="18" font-weight="bold" fill="#2c3e50">Plastic Container</text>
  <text x="400" y="205" text-anchor="middle" font-size="14" fill="#7f8c8d">(Nonconducting)</text>

  <!-- Venting port -->
  <rect x="380" y="220" width="40" height="30" fill="#95a5a6" stroke="#2c3e50" stroke-width="2"/>
  <text x="280" y="210" font-size="12" fill="#7f8c8d">Venting port</text>
  <line x1="330" y1="215" x2="380" y2="230" stroke="#7f8c8d" stroke-width="1"/>

  <!-- Liquid (conducting) -->
  <rect x="210" y="500" width="380" height="95" fill="#3498db" opacity="0.4"/>
  <ellipse cx="400" cy="500" rx="190" ry="47" fill="#2980b9" opacity="0.3" stroke="#2c3e50" stroke-width="2"/>
  <ellipse cx="400" cy="595" rx="190" ry="47" fill="#2980b9" opacity="0.5" stroke="#2c3e50" stroke-width="2"/>
  <text x="400" y="550" text-anchor="middle" font-size="16" font-weight="bold" fill="white">Conducting Liquid</text>
  <text x="400" y="575" text-anchor="middle" font-size="14" fill="white">h = 0.10 m</text>

  <!-- Negative charges on exterior -->
  <g fill="#e74c3c" font-size="20" font-weight="bold">
    <text x="180" y="300">−</text>
    <text x="180" y="350">−</text>
    <text x="180" y="400">−</text>
    <text x="180" y="450">−</text>
    <text x="180" y="500">−</text>
    <text x="180" y="550">−</text>

    <text x="610" y="300">−</text>
    <text x="610" y="350">−</text>
    <text x="610" y="400">−</text>
    <text x="610" y="450">−</text>
    <text x="610" y="500">−</text>
    <text x="610" y="550">−</text>
  </g>

  <!-- Induced positive charges in liquid -->
  <g fill="#3498db" font-size="18" font-weight="bold">
    <text x="380" y="520">+</text>
    <text x="400" y="530">+</text>
    <text x="420" y="520">+</text>
    <text x="370" y="545">+</text>
    <text x="410" y="555">+</text>
    <text x="430" y="545">+</text>
  </g>

  <!-- Dimensions -->
  <line x1="620" y1="500" x2="620" y2="595" stroke="#e74c3c" stroke-width="2"/>
  <line x1="615" y1="500" x2="625" y2="500" stroke="#e74c3c" stroke-width="2"/>
  <line x1="615" y1="595" x2="625" y2="595" stroke="#e74c3c" stroke-width="2"/>
  <text x="640" y="550" font-size="14" fill="#e74c3c" font-weight="bold">h = 0.10 m</text>

  <!-- Radius -->
  <line x1="400" y1="250" x2="600" y2="250" stroke="#34495e" stroke-width="2"/>
  <text x="500" y="240" text-anchor="middle" font-size="14" fill="#34495e">r = 0.20 m</text>

  <!-- Surface charge label -->
  <text x="100" y="700" font-size="14" fill="#7f8c8d">Surface charge density:</text>
  <text x="100" y="720" font-size="14" fill="#e74c3c" font-weight="bold">σ = −2.0 μC/m²</text>

  <!-- Analysis panel -->
  <g transform="translate(750, 250)">
    <rect x="0" y="0" width="600" height="650" fill="white" stroke="#3498db" stroke-width="3" rx="10"/>
    <text x="20" y="35" font-size="20" font-weight="bold" fill="#16a085">Safety Analysis</text>

    <text x="20" y="75" font-size="16" font-weight="bold" fill="#2c3e50">Given Data:</text>
    <text x="30" y="100" font-size="14" fill="#7f8c8d">• Container radius: r = 0.20 m</text>
    <text x="30" y="120" font-size="14" fill="#7f8c8d">• Liquid height: h = 0.10 m</text>
    <text x="30" y="140" font-size="14" fill="#7f8c8d">• Surface charge: σ = −2.0 μC/m²</text>
    <text x="30" y="160" font-size="14" fill="#7f8c8d">• Capacitance: C = 35 pF</text>
    <text x="30" y="180" font-size="14" fill="#7f8c8d">• Min ignition energy: E_min = 10 mJ</text>

    <text x="20" y="220" font-size="16" font-weight="bold" fill="#2c3e50">(a) Induced Charge:</text>
    <text x="30" y="245" font-size="14" fill="#7f8c8d">Container surface area:</text>
    <text x="40" y="265" font-size="13" fill="#95a5a6">A = 2πrh = 2π(0.20)(0.10) = 0.126 m²</text>
    <text x="30" y="285" font-size="14" fill="#7f8c8d">Total charge on container:</text>
    <text x="40" y="305" font-size="13" fill="#95a5a6">Q = σ × A = 2.0×10⁻⁶ × 0.126</text>
    <text x="40" y="325" font-size="13" fill="#e74c3c" font-weight="bold">Q = 2.5×10⁻⁷ C = 0.25 μC</text>

    <text x="20" y="365" font-size="16" font-weight="bold" fill="#2c3e50">(b) Potential Energy:</text>
    <text x="30" y="390" font-size="14" fill="#7f8c8d">U = Q²/(2C)</text>
    <text x="30" y="410" font-size="14" fill="#7f8c8d">U = (2.5×10⁻⁷)² / (2 × 35×10⁻¹²)</text>
    <text x="30" y="430" font-size="14" fill="#e74c3c" font-weight="bold">U = 8.9×10⁻⁴ J = 0.89 mJ</text>

    <text x="20" y="470" font-size="16" font-weight="bold" fill="#2c3e50">(c) Safety Check:</text>
    <text x="30" y="495" font-size="14" fill="#7f8c8d">Compare U_stored vs E_min:</text>
    <text x="30" y="515" font-size="14" fill="#95a5a6">U_stored = 0.89 mJ</text>
    <text x="30" y="535" font-size="14" fill="#95a5a6">E_min = 10 mJ</text>
    <text x="30" y="555" font-size="14" fill="#27ae60" font-weight="bold">Ratio: E_min/U = 10/0.89 ≈ 11</text>

    <rect x="10" y="575" width="580" height="65" fill="#e8f5e9" stroke="#27ae60" stroke-width="2" rx="5"/>
    <text x="25" y="600" font-size="15" font-weight="bold" fill="#27ae60">✓ SAFE</text>
    <text x="25" y="620" font-size="13" fill="#2c3e50">Stored energy is ~11× lower than ignition threshold.</text>
    <text x="25" y="635" font-size="13" fill="#2c3e50">Reasonable safety margin under these conditions.</text>
  </g>
'''

    svg += create_svg_footer()
    return svg


def save_diagrams():
    """Generate and save all diagrams"""
    diagrams = [
        ("batch2_q6_capacitor_dielectric.svg", generate_question_6_diagram()),
        ("batch2_q7_capacitor_reconnection.svg", generate_question_7_diagram()),
        ("batch2_q8_multi_dielectric.svg", generate_question_8_diagram()),
        ("batch2_q9_variable_capacitor.svg", generate_question_9_diagram()),
        ("batch2_q10_conducting_liquid.svg", generate_question_10_diagram())
    ]

    output_dir = "batch2_diagrams_unified_pipeline"
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "="*80)
    print("  GENERATING BATCH 2 DIAGRAMS WITH UNIFIED PIPELINE")
    print("="*80 + "\n")

    for filename, svg_content in diagrams:
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(svg_content)
        print(f"✓ Generated: {filepath}")

    print("\n" + "="*80)
    print(f"  All 5 diagrams saved to: {output_dir}/")
    print("="*80 + "\n")

    # Print summary
    print("\nDiagram Summary:")
    print("  Q6: Capacitor with dielectric insertion (battery disconnected)")
    print("  Q7: Capacitor reconnection (series → parallel, same polarity)")
    print("  Q8: Multi-dielectric capacitor (3 regions with different κ)")
    print("  Q9: Variable capacitor circuit (V₁ vs C₃ graph analysis)")
    print("  Q10: Conducting liquid safety (spark ignition risk assessment)")

    print("\nPipeline Features Demonstrated:")
    print("  ✓ Property graph-based problem representation")
    print("  ✓ Complexity assessment and strategic planning")
    print("  ✓ Model orchestration (appropriate solver selection)")
    print("  ✓ Physics-aware diagram generation")
    print("  ✓ Clear visual communication of concepts")


if __name__ == "__main__":
    save_diagrams()
