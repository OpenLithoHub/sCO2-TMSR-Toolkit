"""CAD geometry generators for sCO₂-TMSR-Toolkit CFD cases.

Each module emits a `constant/triSurface/*.stl` for a specific case, with no
external CAD library dependencies. Run from repo root:

    python -m tools.cad.zigzag                # case02 zigzag channel
"""
