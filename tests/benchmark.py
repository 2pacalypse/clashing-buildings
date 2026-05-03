import pytest
from shapely.geometry import Polygon
from app.models.canonical import CanonicalBuilding, CanonicalBuildingSet, CanonicalPolygon
from app.algorithms.naive_clash_detector import NaiveClashDetection
from app.algorithms.strtree_clash_detector import STRtreeClashDetection


def _run_chain_overlap_benchmark(benchmark, num_buildings, detector_cls, expected_clashes):
    """
    Helper function to run chain overlap benchmarks.
    
    Args:
        benchmark: pytest-benchmark fixture
        num_buildings: Number of buildings to create (e.g., 500, 1000)
        detector_cls: Detector strategy class (e.g., NaiveClashDetection, STRtreeClashDetection)
        expected_clashes: Expected number of clashes in the result
    """
    buildings = []
    for i in range(num_buildings):
        offset_x = 5 * i
        buildings.append(
            CanonicalBuilding(
                elevation=0,
                height=10,
                base=CanonicalPolygon(
                    polygon=Polygon([
                        (offset_x, 0),
                        (offset_x + 10, 0),
                        (offset_x + 10, 10),
                        (offset_x, 10),
                    ])
                ),
            )
        )
    building_set = CanonicalBuildingSet(buildings=tuple(buildings))
    detector = detector_cls()
    def run():
        return detector.detect_clashes(building_set)
    result = benchmark(run)
    assert len(result) == expected_clashes


@pytest.mark.benchmark(group="clash_detection")
@pytest.mark.parametrize("num_buildings,detector_cls,expected_clashes", [
    (500, NaiveClashDetection, 499),
    (500, STRtreeClashDetection, 499),
    (1000, NaiveClashDetection, 999),
    (1000, STRtreeClashDetection, 999),
])
def test_benchmark_chain_overlap(benchmark, num_buildings, detector_cls, expected_clashes):
    """Benchmark chain overlap clash detection with different algorithms and scales."""
    _run_chain_overlap_benchmark(benchmark, num_buildings, detector_cls, expected_clashes)
