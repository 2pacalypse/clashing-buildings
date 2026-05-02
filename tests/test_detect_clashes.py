import pytest
from shapely.geometry import Polygon
from app.algorithms.clash_detector import detect_clashes
from app.models.canonical import (
    CanonicalBuilding,
    CanonicalBuildingSet,
    CanonicalPolygon,
    CanonicalBuildingIntersection,
)


class TestDetectClashes:
    def test_two_buildings_100000_vertices(self):
        """Test with 2 buildings, each with 100,000 vertices (very large polygons)."""
        import math

        def make_circle_polygon(center_x, center_y, radius, num_vertices):
            return [
                (
                    center_x + radius * math.cos(2 * math.pi * i / num_vertices),
                    center_y + radius * math.sin(2 * math.pi * i / num_vertices),
                )
                for i in range(num_vertices)
            ]

        num_vertices = 100000
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

    def test_two_buildings_200000_vertices(self):
        """Test with 2 buildings, each with 200,000 vertices (very large polygons)."""
        import math

        def make_circle_polygon(center_x, center_y, radius, num_vertices):
            return [
                (
                    center_x + radius * math.cos(2 * math.pi * i / num_vertices),
                    center_y + radius * math.sin(2 * math.pi * i / num_vertices),
                )
                for i in range(num_vertices)
            ]

        num_vertices = 200000
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

    def test_two_buildings_300000_vertices(self):
        """Test with 2 buildings, each with 300,000 vertices (very large polygons)."""
        import math

        def make_circle_polygon(center_x, center_y, radius, num_vertices):
            return [
                (
                    center_x + radius * math.cos(2 * math.pi * i / num_vertices),
                    center_y + radius * math.sin(2 * math.pi * i / num_vertices),
                )
                for i in range(num_vertices)
            ]

        num_vertices = 300000
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

    def test_two_buildings_400000_vertices(self):
        """Test with 2 buildings, each with 400,000 vertices (very large polygons)."""
        import math

        def make_circle_polygon(center_x, center_y, radius, num_vertices):
            return [
                (
                    center_x + radius * math.cos(2 * math.pi * i / num_vertices),
                    center_y + radius * math.sin(2 * math.pi * i / num_vertices),
                )
                for i in range(num_vertices)
            ]

        num_vertices = 400000
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

    def test_two_buildings_500000_vertices(self):
        """Test with 2 buildings, each with 500,000 vertices (very large polygons)."""
        import math

        def make_circle_polygon(center_x, center_y, radius, num_vertices):
            return [
                (
                    center_x + radius * math.cos(2 * math.pi * i / num_vertices),
                    center_y + radius * math.sin(2 * math.pi * i / num_vertices),
                )
                for i in range(num_vertices)
            ]

        num_vertices = 500000
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

    def test_two_buildings_10000_vertices(self):
        """Test with 2 buildings, each with 10,000 vertices (large polygons)."""
        import math

        def make_circle_polygon(center_x, center_y, radius, num_vertices):
            return [
                (
                    center_x + radius * math.cos(2 * math.pi * i / num_vertices),
                    center_y + radius * math.sin(2 * math.pi * i / num_vertices),
                )
                for i in range(num_vertices)
            ]

        num_vertices = 10000
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

    def test_two_buildings_20000_vertices(self):
        """Test with 2 buildings, each with 20,000 vertices (very large polygons)."""
        import math

        def make_circle_polygon(center_x, center_y, radius, num_vertices):
            return [
                (
                    center_x + radius * math.cos(2 * math.pi * i / num_vertices),
                    center_y + radius * math.sin(2 * math.pi * i / num_vertices),
                )
                for i in range(num_vertices)
            ]

        num_vertices = 20000
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

    def test_two_buildings_30000_vertices(self):
        """Test with 2 buildings, each with 30,000 vertices (extremely large polygons)."""
        import math

        def make_circle_polygon(center_x, center_y, radius, num_vertices):
            return [
                (
                    center_x + radius * math.cos(2 * math.pi * i / num_vertices),
                    center_y + radius * math.sin(2 * math.pi * i / num_vertices),
                )
                for i in range(num_vertices)
            ]

        num_vertices = 30000
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

    def test_two_buildings_many_vertices(self):
        """Test with 2 buildings, each with 5000 vertices (large polygons)."""
        import math

        def make_circle_polygon(center_x, center_y, radius, num_vertices):
            return [
                (
                    center_x + radius * math.cos(2 * math.pi * i / num_vertices),
                    center_y + radius * math.sin(2 * math.pi * i / num_vertices),
                )
                for i in range(num_vertices)
            ]

        num_vertices = 5000
        poly1 = Polygon(make_circle_polygon(0, 0, 10, num_vertices))
        poly2 = Polygon(
            make_circle_polygon(5, 0, 10, num_vertices)
        )  # Overlapping circles
        building1 = CanonicalBuilding(
            elevation=0, height=10, base=CanonicalPolygon(polygon=poly1)
        )
        building2 = CanonicalBuilding(
            elevation=0, height=10, base=CanonicalPolygon(polygon=poly2)
        )
        building_set = CanonicalBuildingSet(buildings=(building1, building2))
        clashes = detect_clashes(building_set)
        assert len(clashes) == 1
        # The intersection should not be empty and should be a polygon
        assert not clashes[0].intersection.base.polygon.is_empty

    def test_200_fully_overlapping_buildings(self):
        """Test with 200 fully overlapping buildings (should be slow, many clashes)."""
        buildings = [
            CanonicalBuilding(
                elevation=0,
                height=10,
                base=CanonicalPolygon(
                    polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
                ),
            )
            for _ in range(200)
        ]
        building_set = CanonicalBuildingSet(buildings=tuple(buildings))
        clashes = detect_clashes(building_set)
        assert len(clashes) == 19900  # 200*199/2

    def test_300_fully_overlapping_buildings(self):
        """Test with 300 fully overlapping buildings (should be slow, many clashes)."""
        buildings = [
            CanonicalBuilding(
                elevation=0,
                height=10,
                base=CanonicalPolygon(
                    polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
                ),
            )
            for _ in range(300)
        ]
        building_set = CanonicalBuildingSet(buildings=tuple(buildings))
        clashes = detect_clashes(building_set)
        assert len(clashes) == 44850  # 300*299/2

    def test_400_fully_overlapping_buildings(self):
        """Test with 400 fully overlapping buildings (should be slow, many clashes)."""
        buildings = [
            CanonicalBuilding(
                elevation=0,
                height=10,
                base=CanonicalPolygon(
                    polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
                ),
            )
            for _ in range(400)
        ]
        building_set = CanonicalBuildingSet(buildings=tuple(buildings))
        clashes = detect_clashes(building_set)
        assert len(clashes) == 79800  # 400*399/2

    def test_500_fully_overlapping_buildings(self):
        """Test with 500 fully overlapping buildings (should be slow, many clashes)."""
        buildings = [
            CanonicalBuilding(
                elevation=0,
                height=10,
                base=CanonicalPolygon(
                    polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
                ),
            )
            for _ in range(500)
        ]
        building_set = CanonicalBuildingSet(buildings=tuple(buildings))
        clashes = detect_clashes(building_set)
        assert len(clashes) == 124750  # 500*499/2

    def test_many_non_overlapping_buildings(self):
        """Test with 100 non-overlapping buildings (should be slow, no clashes)."""
        buildings = []
        for i in range(100):
            offset = i * 20
            buildings.append(
                CanonicalBuilding(
                    elevation=0,
                    height=10,
                    base=CanonicalPolygon(
                        polygon=Polygon(
                            [
                                (offset, 0),
                                (offset + 10, 0),
                                (offset + 10, 10),
                                (offset, 10),
                            ]
                        )
                    ),
                )
            )
        building_set = CanonicalBuildingSet(buildings=tuple(buildings))
        clashes = detect_clashes(building_set)
        assert len(clashes) == 0

    def test_many_overlapping_buildings(self):
        """Test with 100 fully overlapping buildings (should be slow, many clashes)."""
        buildings = []
        for i in range(100):
            buildings.append(
                CanonicalBuilding(
                    elevation=0,
                    height=10,
                    base=CanonicalPolygon(
                        polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
                    ),
                )
            )
        building_set = CanonicalBuildingSet(buildings=tuple(buildings))
        clashes = detect_clashes(building_set)
        # Number of unique pairs: n * (n-1) / 2
        assert len(clashes) == 4950

    """Unit tests for the detect_clashes method."""

    def test_no_clashes_non_overlapping_buildings(self):
        """Test that non-overlapping buildings produce no clashes."""
        building1 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
            ),
        )
        building2 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(20, 20), (30, 20), (30, 30), (20, 30)])
            ),
        )
        building_set = CanonicalBuildingSet(buildings=(building1, building2))

        clashes = detect_clashes(building_set)
        assert len(clashes) == 0

    def test_clash_2d_overlapping_same_elevation_height(self):
        """Test that 2D overlapping buildings with same elevation and height produce clash."""
        building1 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
            ),
        )
        building2 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(5, 5), (15, 5), (15, 15), (5, 15)])
            ),
        )
        building_set = CanonicalBuildingSet(buildings=(building1, building2))

        clashes = detect_clashes(building_set)
        assert len(clashes) == 1
        clash = clashes[0]
        assert clash.building_ids == (0, 1)
        assert clash.intersection.elevation == 0
        assert clash.intersection.height == 10

    def test_no_clash_2d_overlap_no_3d_overlap(self):
        """Test that 2D overlapping buildings with no 3D overlap produce no clash."""
        # Building 1: elevation 0-10
        building1 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
            ),
        )
        # Building 2: elevation 10-20 (stacked on top, no overlap)
        building2 = CanonicalBuilding(
            elevation=10,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(5, 5), (15, 5), (15, 15), (5, 15)])
            ),
        )
        building_set = CanonicalBuildingSet(buildings=(building1, building2))

        clashes = detect_clashes(building_set)
        assert len(clashes) == 0

    def test_clash_partial_3d_overlap(self):
        """Test 2D overlapping buildings with partial 3D overlap."""
        # Building 1: elevation 0-15
        building1 = CanonicalBuilding(
            elevation=0,
            height=15,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
            ),
        )
        # Building 2: elevation 10-20 (overlaps building 1 from 10-15)
        building2 = CanonicalBuilding(
            elevation=10,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(5, 5), (15, 5), (15, 15), (5, 15)])
            ),
        )
        building_set = CanonicalBuildingSet(buildings=(building1, building2))

        clashes = detect_clashes(building_set)
        assert len(clashes) == 1
        clash = clashes[0]
        assert clash.intersection.elevation == 10  # max(0, 10)
        assert clash.intersection.height == 5  # min(15, 20) - 10

    def test_single_building_no_clash(self):
        """Test that a single building produces no clashes."""
        building = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
            ),
        )
        building_set = CanonicalBuildingSet(buildings=(building,))

        clashes = detect_clashes(building_set)
        assert len(clashes) == 0

    def test_empty_building_set_no_clash(self):
        """Test that an empty building set produces no clashes."""
        building_set = CanonicalBuildingSet(buildings=())

        clashes = detect_clashes(building_set)
        assert len(clashes) == 0

    def test_multiple_clashes(self):
        """Test detection of multiple clashes in a set of buildings."""
        # Building 1 at (0, 0)
        building1 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
            ),
        )
        # Building 2 at (5, 5) - overlaps with building 1
        building2 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(5, 5), (15, 5), (15, 15), (5, 15)])
            ),
        )
        # Building 3 at (8, 8) - overlaps with both building 1 and 2
        building3 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(8, 8), (18, 8), (18, 18), (8, 18)])
            ),
        )
        building_set = CanonicalBuildingSet(buildings=(building1, building2, building3))

        clashes = detect_clashes(building_set)
        assert len(clashes) == 3  # 1-2, 1-3, 2-3

    def test_touching_boundaries_no_clash(self):
        """Test that buildings touching at boundaries produce no clash."""
        # Building 1: (0,0) to (10,10)
        building1 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
            ),
        )
        # Building 2: (10,0) to (20,10) - touching at edge
        building2 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(10, 0), (20, 0), (20, 10), (10, 10)])
            ),
        )
        building_set = CanonicalBuildingSet(buildings=(building1, building2))

        clashes = detect_clashes(building_set)
        # Touching at boundary should not create a clash (intersection area is 0)
        assert len(clashes) == 0

    def test_clash_properties_intersection_geometry(self):
        """Test that clash intersection has correct geometry properties."""
        # 5x5 square at (0,0)
        building1 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(polygon=Polygon([(0, 0), (5, 0), (5, 5), (0, 5)])),
        )
        # 5x5 square at (2,2) - overlaps with 3x3 area
        building2 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(polygon=Polygon([(2, 2), (7, 2), (7, 7), (2, 7)])),
        )
        building_set = CanonicalBuildingSet(buildings=(building1, building2))

        clashes = detect_clashes(building_set)
        assert len(clashes) == 1

        clash = clashes[0]
        # Intersection should be 3x3 square at (2,2)
        intersection_area = clash.intersection.base.polygon.area
        assert abs(intersection_area - 9.0) < 0.01  # 3x3 = 9 square units

    def test_clash_correct_elevation_height_range(self):
        """Test that clash reports correct elevation and height ranges."""
        # Building 1: ground level 0, height 20 (0-20)
        building1 = CanonicalBuilding(
            elevation=0,
            height=20,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
            ),
        )
        # Building 2: elevated 5, height 15 (5-20)
        building2 = CanonicalBuilding(
            elevation=5,
            height=15,
            base=CanonicalPolygon(
                polygon=Polygon([(5, 5), (15, 5), (15, 15), (5, 15)])
            ),
        )
        building_set = CanonicalBuildingSet(buildings=(building1, building2))

        clashes = detect_clashes(building_set)
        assert len(clashes) == 1
        clash = clashes[0]
        # Overlap is from max(0,5)=5 to min(20,20)=20
        assert clash.intersection.elevation == 5
        assert clash.intersection.height == 15  # 20 - 5

    def test_clash_building_ids_in_correct_order(self):
        """Test that building IDs are in correct order (i, j) with i < j."""
        building1 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
            ),
        )
        building2 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(5, 5), (15, 5), (15, 15), (5, 15)])
            ),
        )
        building_set = CanonicalBuildingSet(buildings=(building1, building2))

        clashes = detect_clashes(building_set)
        assert len(clashes) == 1
        assert clashes[0].building_ids == (0, 1)

    def test_complex_polygon_shapes(self):
        """Test clash detection with complex (non-rectangular) polygon shapes."""
        # Triangle building 1
        building1 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(polygon=Polygon([(0, 0), (10, 0), (5, 10)])),
        )
        # Triangle building 2 - overlapping
        building2 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(polygon=Polygon([(5, 0), (15, 0), (10, 10)])),
        )
        building_set = CanonicalBuildingSet(buildings=(building1, building2))

        clashes = detect_clashes(building_set)
        assert len(clashes) == 1
        assert not clashes[0].intersection.base.polygon.is_empty

    def test_zero_height_clash_not_reported(self):
        """Test that clashes with zero height overlap are not reported."""
        # Building 1: 0-10
        building1 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
            ),
        )
        # Building 2: 10-20 (touches at top, no volume overlap)
        building2 = CanonicalBuilding(
            elevation=10,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(5, 5), (15, 5), (15, 15), (5, 15)])
            ),
        )
        building_set = CanonicalBuildingSet(buildings=(building1, building2))

        clashes = detect_clashes(building_set)
        assert len(clashes) == 0

    def test_four_buildings_all_overlapping(self):
        """Test clash detection with four buildings all overlapping at center."""
        # Building 1: quadrant top-left
        building1 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 5), (10, 5), (10, 15), (0, 15)])
            ),
        )
        # Building 2: quadrant top-right
        building2 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(5, 5), (15, 5), (15, 15), (5, 15)])
            ),
        )
        # Building 3: quadrant bottom-left
        building3 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
            ),
        )
        # Building 4: quadrant bottom-right
        building4 = CanonicalBuilding(
            elevation=0,
            height=10,
            base=CanonicalPolygon(
                polygon=Polygon([(5, 0), (15, 0), (15, 10), (5, 10)])
            ),
        )
        building_set = CanonicalBuildingSet(
            buildings=(building1, building2, building3, building4)
        )

        clashes = detect_clashes(building_set)
        # All pairs overlap: (0,1), (0,2), (0,3), (1,2), (1,3), (2,3) = 6 clashes
        assert len(clashes) == 6
