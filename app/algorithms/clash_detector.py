"""
Algorithms for detecting geometric clashes between buildings using canonical models.
"""

from typing import List

from app.algorithms.naive_clash_detector import NaiveClashDetection
from app.algorithms.strtree_clash_detector import STRtreeClashDetection
from app.models.canonical import (
    CanonicalBuildingIntersection,
    CanonicalBuildingSet,
)


def detect_clashes(
    building_set: CanonicalBuildingSet,
) -> List[CanonicalBuildingIntersection]:
    """Run clash detection using the default strategy."""
    return STRtreeClashDetection().detect_clashes(building_set)
