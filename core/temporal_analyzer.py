"""
Temporal Stage Analyzer - Generic multi-stage problem detection for all physics domains

Handles:
- Multi-stage problems (before/after, initial/final)
- Temporal transitions (connected → disconnected, moving → stopped)
- Implicit state changes (same signs → parallel, in contact → collision)
- Stage identification (which stage does the question ask about?)

Works across ALL domains:
- Mechanics: before collision → after collision
- Electrostatics: series → disconnected → parallel
- Thermodynamics: initial state → compressed → final state
- Optics: object → through lens → image
- Waves: before interference → during → after
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class TemporalStage(Enum):
    """Represents different stages in a multi-stage problem"""
    INITIAL = "initial"
    INTERMEDIATE = "intermediate"
    FINAL = "final"
    CURRENT = "current"  # For static problems


class TransitionType(Enum):
    """Types of transitions between stages"""
    CONNECTION_CHANGE = "connection_change"  # connected → disconnected, series → parallel
    STATE_CHANGE = "state_change"  # compressed → expanded, heated → cooled
    MOTION_CHANGE = "motion_change"  # moving → stopped, before collision → after
    CONFIGURATION_CHANGE = "configuration_change"  # object position → image position
    INTERACTION_CHANGE = "interaction_change"  # separate → in contact, interfering


@dataclass
class Stage:
    """Represents a single stage in a multi-stage problem"""
    stage_type: TemporalStage
    description: str
    keywords: List[str]
    transition_from: Optional['Stage'] = None
    transition_type: Optional[TransitionType] = None
    is_question_target: bool = False  # Does the question ask about this stage?


class TemporalAnalyzer:
    """Analyzes problem text to identify temporal stages and transitions"""

    def __init__(self):
        # Keywords indicating multi-stage problems
        self.stage_indicators = {
            TemporalStage.INITIAL: [
                'initially', 'at first', 'before', 'originally', 'starts',
                'beginning', 'first', 'at t=0', 'prior to'
            ],
            TemporalStage.INTERMEDIATE: [
                'then', 'next', 'subsequently', 'after that', 'during',
                'while', 'as', 'when'
            ],
            TemporalStage.FINAL: [
                'finally', 'at the end', 'after', 'ultimately', 'eventually',
                'in the end', 'resulting', 'ends up'
            ]
        }

        # Transition keywords by type
        self.transition_patterns = {
            TransitionType.CONNECTION_CHANGE: {
                'disconnect': ['disconnect', 'disconnected', 'remove', 'removed', 'separate', 'separated'],
                'reconnect': ['reconnect', 'reconnected', 'connect again', 'connected again'],
                'series_to_parallel': ['same sign', 'positive to positive', 'negative to negative',
                                      'like charges', 'like plates', '+ve to +ve', '-ve to -ve'],
                'parallel_to_series': ['opposite sign', 'positive to negative', 'different polarity']
            },
            TransitionType.STATE_CHANGE: {
                'compress': ['compress', 'compressed', 'squeeze', 'reduced volume'],
                'expand': ['expand', 'expanded', 'increase volume'],
                'heat': ['heat', 'heated', 'warm', 'temperature increase'],
                'cool': ['cool', 'cooled', 'temperature decrease'],
                'melt': ['melt', 'melted', 'liquify'],
                'freeze': ['freeze', 'frozen', 'solidify']
            },
            TransitionType.MOTION_CHANGE: {
                'collision': ['collide', 'collision', 'hit', 'strike', 'impact'],
                'start_moving': ['start', 'begins moving', 'accelerate'],
                'stop_moving': ['stop', 'comes to rest', 'halts', 'stops'],
                'release': ['release', 'released', 'let go', 'dropped']
            },
            TransitionType.CONFIGURATION_CHANGE: {
                'through_lens': ['through', 'pass through', 'transmitted'],
                'reflect': ['reflect', 'reflected', 'bounce'],
                'refract': ['refract', 'refracted', 'bend'],
                'focus': ['focus', 'focused', 'converge']
            },
            TransitionType.INTERACTION_CHANGE: {
                'contact': ['touch', 'in contact', 'touching', 'pressed against'],
                'separate': ['separate', 'apart', 'no longer touching'],
                'interfere': ['interfere', 'interference', 'superpose'],
                'combine': ['combine', 'mix', 'merge']
            }
        }

        # Question target indicators (what stage does the question ask about?)
        self.question_indicators = {
            TemporalStage.INITIAL: [
                'what was the initial', 'before the', 'at the start'
            ],
            TemporalStage.FINAL: [
                'what is', 'what will be', 'find the final', 'after the',
                'resulting', 'at the end', 'eventually'
            ]
        }

    def analyze(self, problem_text: str) -> Dict:
        """
        Analyze problem text to identify temporal stages and transitions

        Args:
            problem_text: The problem description

        Returns:
            Dictionary containing:
            - is_multistage: bool
            - stages: List[Stage]
            - question_target_stage: TemporalStage
            - transitions: List[TransitionType]
            - implicit_relationships: Dict[str, str]
        """
        text_lower = problem_text.lower()

        # Detect if this is a multi-stage problem
        is_multistage = self._is_multistage(text_lower)

        if not is_multistage:
            return {
                'is_multistage': False,
                'stages': [Stage(TemporalStage.CURRENT, "Single stage problem", [], is_question_target=True)],
                'question_target_stage': TemporalStage.CURRENT,
                'transitions': [],
                'implicit_relationships': {}
            }

        # Identify stages
        stages = self._identify_stages(text_lower, problem_text)

        # Identify transitions
        transitions = self._identify_transitions(text_lower)

        # Determine which stage the question asks about
        question_target_stage = self._identify_question_target(text_lower, stages)

        # Detect implicit relationships
        implicit_relationships = self._detect_implicit_relationships(text_lower)

        return {
            'is_multistage': True,
            'stages': stages,
            'question_target_stage': question_target_stage,
            'transitions': transitions,
            'implicit_relationships': implicit_relationships
        }

    def _is_multistage(self, text: str) -> bool:
        """Detect if problem describes multiple stages"""
        # Check for stage indicators
        stage_count = 0
        for stage_type, keywords in self.stage_indicators.items():
            if any(keyword in text for keyword in keywords):
                stage_count += 1

        # Check for transition indicators
        has_transition = False
        for transition_type, patterns in self.transition_patterns.items():
            for pattern_name, keywords in patterns.items():
                if any(keyword in text for keyword in keywords):
                    has_transition = True
                    break

        # Multi-stage if: multiple stage indicators OR has transitions
        return stage_count >= 2 or has_transition

    def _identify_stages(self, text_lower: str, text_original: str) -> List[Stage]:
        """Identify distinct stages in the problem"""
        stages = []

        # Find sentences/clauses for each stage
        for stage_type, keywords in self.stage_indicators.items():
            stage_keywords = [kw for kw in keywords if kw in text_lower]
            if stage_keywords:
                # Extract description around keywords
                description = self._extract_stage_description(text_original, stage_keywords[0])
                stages.append(Stage(
                    stage_type=stage_type,
                    description=description,
                    keywords=stage_keywords
                ))

        # If no explicit stage markers, infer from transitions
        if not stages:
            stages = self._infer_stages_from_transitions(text_lower)

        return sorted(stages, key=lambda s: s.stage_type.value)

    def _identify_transitions(self, text: str) -> List[TransitionType]:
        """Identify types of transitions in the problem"""
        transitions = []

        for transition_type, patterns in self.transition_patterns.items():
            for pattern_name, keywords in patterns.items():
                if any(keyword in text for keyword in keywords):
                    if transition_type not in transitions:
                        transitions.append(transition_type)
                    break

        return transitions

    def _identify_question_target(self, text: str, stages: List[Stage]) -> TemporalStage:
        """Determine which stage the question asks about"""
        # Check question indicators
        for stage_type, indicators in self.question_indicators.items():
            if any(indicator in text for indicator in indicators):
                # Mark this stage as the target
                for stage in stages:
                    if stage.stage_type == stage_type:
                        stage.is_question_target = True
                return stage_type

        # Default: assume question asks about FINAL state
        if stages:
            stages[-1].is_question_target = True
            return stages[-1].stage_type

        return TemporalStage.CURRENT

    def _detect_implicit_relationships(self, text: str) -> Dict[str, str]:
        """Detect implicit relationships/connections described in text"""
        relationships = {}

        # Connection patterns
        if any(pattern in text for pattern in ['same sign', 'positive to positive', 'negative to negative']):
            relationships['circuit_topology'] = 'parallel'

        if any(pattern in text for pattern in ['opposite sign', 'positive to negative']):
            relationships['circuit_topology'] = 'series'

        # Contact/collision patterns
        if any(pattern in text for pattern in ['touch', 'in contact', 'pressed against']):
            relationships['mechanical_interaction'] = 'contact'

        if any(pattern in text for pattern in ['collide', 'collision', 'strike']):
            relationships['mechanical_interaction'] = 'collision'

        # Optical patterns
        if any(pattern in text for pattern in ['through', 'pass through']):
            relationships['optical_path'] = 'transmission'

        if 'reflect' in text or 'bounce' in text:
            relationships['optical_path'] = 'reflection'

        # Thermal patterns
        if any(pattern in text for pattern in ['in contact', 'thermal equilibrium']):
            relationships['thermal_interaction'] = 'heat_transfer'

        return relationships

    def _extract_stage_description(self, text: str, keyword: str) -> str:
        """Extract description of a stage from text"""
        # Find the sentence containing the keyword
        sentences = text.split('.')
        for sentence in sentences:
            if keyword.lower() in sentence.lower():
                return sentence.strip()
        return ""

    def _infer_stages_from_transitions(self, text: str) -> List[Stage]:
        """Infer stages when no explicit markers exist"""
        stages = []

        # Look for transitional words
        if 'then' in text or 'after' in text:
            stages.append(Stage(TemporalStage.INITIAL, "Before transition", []))
            stages.append(Stage(TemporalStage.FINAL, "After transition", ['then', 'after']))

        return stages


class TemporalSceneSelector:
    """Selects which temporal stage to visualize"""

    def __init__(self):
        pass

    def select_stage_to_render(self, temporal_analysis: Dict, domain: str = None) -> TemporalStage:
        """
        Determine which stage should be visualized in the diagram

        Args:
            temporal_analysis: Output from TemporalAnalyzer
            domain: Physics domain (optional, for domain-specific rules)

        Returns:
            TemporalStage to render
        """
        if not temporal_analysis['is_multistage']:
            return TemporalStage.CURRENT

        # Use the question target stage
        return temporal_analysis['question_target_stage']

    def should_render_multiple_stages(self, temporal_analysis: Dict) -> bool:
        """Determine if multiple stages should be shown (multi-panel diagram)"""
        # Show multiple stages if:
        # 1. Problem has 2+ distinct stages
        # 2. Understanding requires seeing the transition
        stages = temporal_analysis['stages']
        transitions = temporal_analysis['transitions']

        # For now, render single stage (target stage)
        # TODO: Implement multi-panel rendering for complex transitions
        return False
