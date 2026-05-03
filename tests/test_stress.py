"""
Stress tests for clash detection.

These tests verify correctness under high-load scenarios (large polygons, many buildings).
They are slower than functional tests and run separately from the main test suite.
"""

import pytest
import math
from shapely.geometry import Polygon
from app.algorithms.clash_detector import detect_clashes
from app.models.canonical import (
    CanonicalBuilding,
    CanonicalBuildingSet,
    CanonicalPolygon,
)


@pytest.mark.parametrize(
    "num_vertices",
    [5000, 10000, 20000, 30000, 100000, 200000, 300000, 400000, 500000],
)
def test_two_buildings_large_polygon_vertices(num_vertices):
    """Test clash detection with overlapping circular polygons with varying vertex counts."""

    def make_circle_polygon(center_x, center_y, radius, num_vertices):
        return [
            (
                center_x + radius * math.cos(2 * math.pi * i / num_vertices),
                center_y + radius * math.sin(2 * math.pi * i / num_vertices),
            )
            for i in range(num_vertices)
        ]

    poly1 = Polygon(make_circle_polygon(0, 0, 10, num_vertices))
    poly2 = Polygon(make_circle_polygon(5, 0, 10, num_vertices))
    building1 = CanonicalBuilding(
        elevation=0, height=10, base=CanonicalPolygon(polygon=poly1)
    )
    building2 = CanonicalBuilding(
        elevation=0, height=10, base=CanonicalPolygon(polygon=poly2)
    )
    building_set = CanonicalBuildingSet(buildings=(building1, building2))
    clashes = detect_clashes(building_set)
    assert len(clashes) == 1
    assert not clashes[0].intersection.base.polygon.is_empty


@pytest.mark.parametrize(
    "num_buildings,expected_clashes",
    [
        (100, 4950),  # 100 * 99 / 2
        (200, 19900),  # 200 * 199 / 2
        (300, 44850),  # 300 * 299 / 2
        (400, 79800),  # 400 * 399 / 2
        (500, 124750),  # 500 * 499 / 2
    ],
)
def test_fully_overlapping_buildings(num_buildings, expected_clashes):
    """Test clash detection with fully overlapping buildings at different scales."""
    buildings = [
        CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
            ),
        )
        for _ in range(num_buildings)
    ]
    building_set = CanonicalBuildingSet(buildings=tuple(buildings))
    clashes = detect_clashes(building_set)
    assert len(clashes) == expected_clashes
