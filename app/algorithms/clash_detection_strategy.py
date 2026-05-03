"""
Strategy interfaces for clash detection algorithms.
"""

from abc import ABC, abstractmethod
from typing import List

from app.models.canonical import (
    CanonicalBuildingIntersection,
    CanonicalBuildingSet,
)


class ClashDetectionStrategy(ABC):
    """Common interface for clash detection algorithms."""

    @abstractmethod
    def detect_clashes(
        self,
        building_set: CanonicalBuildingSet,
    ) -> List[CanonicalBuildingIntersection]:
        """Return the intersections found in the provided building set."""
