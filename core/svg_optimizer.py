"""
SVG Optimizer
=============

Post-processing optimization for generated SVG diagrams.
Reduces file size and improves rendering performance.

Uses svgo (Node.js) or scour (Python) when available.

Author: Universal STEM Diagram Generator
Date: November 12, 2025
"""

from typing import Optional, Dict, Any
import re
import subprocess
import logging


class SVGOptimizer:
    """
    SVG optimization using external tools or built-in methods

    Supported backends:
    - svgo: Node.js-based optimizer (best quality)
    - scour: Python-based optimizer
    - builtin: Simple regex-based cleanup (fallback)
    """

    def __init__(self, backend: str = "auto"):
        """
        Initialize SVG optimizer

        Args:
            backend: Optimization backend ('svgo', 'scour', 'builtin', 'auto')
        """
        self.logger = logging.getLogger(__name__)
        self.backend = backend

        if backend == "auto":
            # Auto-detect available backend
            if self._check_svgo():
                self.backend = "svgo"
            elif self._check_scour():
                self.backend = "scour"
            else:
                self.backend = "builtin"

        self.logger.info(f"SVG optimizer initialized with backend: {self.backend}")

    def _check_svgo(self) -> bool:
        """Check if svgo is available"""
        try:
            subprocess.run(['svgo', '--version'], capture_output=True, timeout=2)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _check_scour(self) -> bool:
        """Check if scour is available"""
        try:
            import scour
            return True
        except ImportError:
            return False

    def optimize(self, svg_content: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        Optimize SVG content

        Args:
            svg_content: SVG string to optimize
            options: Backend-specific options

        Returns:
            Optimized SVG string

        Example:
            >>> optimizer = SVGOptimizer()
            >>> optimized = optimizer.optimize(svg_content)
            >>> print(f"Reduced by {len(svg_content) - len(optimized)} bytes")
        """
        options = options or {}

        try:
            if self.backend == "svgo":
                return self._optimize_svgo(svg_content, options)
            elif self.backend == "scour":
                return self._optimize_scour(svg_content, options)
            else:
                return self._optimize_builtin(svg_content, options)

        except Exception as e:
            self.logger.error(f"SVG optimization failed: {e}")
            return svg_content  # Return original on error

    def _optimize_svgo(self, svg: str, options: Dict) -> str:
        """Optimize using svgo"""
        try:
            # Write to temp file
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
                f.write(svg)
                temp_path = f.name

            # Run svgo
            result = subprocess.run(
                ['svgo', temp_path, '-o', temp_path, '--multipass'],
                capture_output=True,
                timeout=10,
                text=True
            )

            if result.returncode == 0:
                with open(temp_path, 'r') as f:
                    optimized = f.read()
                os.unlink(temp_path)
                return optimized
            else:
                self.logger.warning(f"svgo failed: {result.stderr}")
                os.unlink(temp_path)
                return svg

        except Exception as e:
            self.logger.error(f"svgo optimization error: {e}")
            return svg

    def _optimize_scour(self, svg: str, options: Dict) -> str:
        """Optimize using scour"""
        try:
            from scour import scour

            # Scour options
            scour_options = scour.generateDefaultOptions()
            scour_options.strip_comments = True
            scour_options.remove_metadata = True
            scour_options.indent_type = 'none'
            scour_options.shorten_ids = True

            # Apply user options
            for key, val in options.items():
                if hasattr(scour_options, key):
                    setattr(scour_options, key, val)

            # Optimize
            optimized = scour.scourString(svg, scour_options)
            return optimized

        except Exception as e:
            self.logger.error(f"scour optimization error: {e}")
            return svg

    def _optimize_builtin(self, svg: str, options: Dict) -> str:
        """
        Built-in optimization using regex cleanup

        Performs simple optimizations:
        - Remove comments
        - Remove unnecessary whitespace
        - Remove empty groups
        - Round coordinates to 2 decimal places
        """
        optimized = svg

        # Remove XML comments
        optimized = re.sub(r'<!--.*?-->', '', optimized, flags=re.DOTALL)

        # Remove unnecessary whitespace between tags
        optimized = re.sub(r'>\s+<', '><', optimized)

        # Remove empty groups
        optimized = re.sub(r'<g[^>]*>\s*</g>', '', optimized)

        # Round coordinates to 2 decimal places (reduces file size)
        def round_number(match):
            try:
                num = float(match.group(1))
                return f'"{round(num, 2)}'
            except:
                return match.group(0)

        optimized = re.sub(r'"([\d.]+)', round_number, optimized)

        # Remove trailing zeros after decimal point
        optimized = re.sub(r'(\d+\.\d*?)0+(["\s,])', r'\1\2', optimized)
        optimized = re.sub(r'(\d+)\.0(["\s,])', r'\1\2', optimized)

        return optimized

    def get_optimization_stats(self, original: str, optimized: str) -> Dict[str, Any]:
        """
        Get optimization statistics

        Args:
            original: Original SVG
            optimized: Optimized SVG

        Returns:
            Dict with size reduction stats
        """
        original_size = len(original)
        optimized_size = len(optimized)
        reduction = original_size - optimized_size
        reduction_pct = (reduction / original_size * 100) if original_size > 0 else 0

        return {
            'original_size': original_size,
            'optimized_size': optimized_size,
            'reduction_bytes': reduction,
            'reduction_percent': round(reduction_pct, 2),
            'backend': self.backend
        }


def optimize_svg(svg_content: str, backend: str = "auto") -> str:
    """
    Convenience function to optimize SVG

    Args:
        svg_content: SVG string
        backend: Optimization backend

    Returns:
        Optimized SVG string
    """
    optimizer = SVGOptimizer(backend=backend)
    return optimizer.optimize(svg_content)
