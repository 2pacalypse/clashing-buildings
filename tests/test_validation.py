"""
Input validation tests for Pydantic models - API layer validation.

Tests verify that invalid inputs are rejected with appropriate error messages.
"""

import pytest
from pydantic import ValidationError
from app.models.clash_detection_request import (
    BuildingProperties,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    ClashDetectionRequest,
)
from app.models.polygon_geometry import PolygonGeometry


# Height validation tests
class TestHeightValidation:
    """Tests for building height validation (must be > 0)."""

    def test_valid_height(self):
        """Height > 0 should be valid."""
        props = BuildingProperties(height=10.5, elevation=0)
        assert props.height == 10.5

    def test_zero_height_rejected(self):
        """Height = 0 should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BuildingProperties(height=0, elevation=0)
        assert "greater than 0" in str(exc_info.value)

    def test_negative_height_rejected(self):
        """Negative height should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BuildingProperties(height=-5, elevation=0)
        assert "greater than 0" in str(exc_info.value)


# Elevation validation tests
class TestElevationValidation:
    """Tests for building elevation validation (must be >= 0)."""

    def test_valid_elevation_zero(self):
        """Elevation = 0 should be valid."""
        props = BuildingProperties(height=10, elevation=0)
        assert props.elevation == 0

    def test_valid_elevation_positive(self):
        """Positive elevation should be valid."""
        props = BuildingProperties(height=10, elevation=5.5)
        assert props.elevation == 5.5

    def test_negative_elevation_rejected(self):
        """Negative elevation should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            BuildingProperties(height=10, elevation=-1)
        assert "greater than or equal to 0" in str(exc_info.value)


# Polygon ring validation tests
class TestPolygonRingValidation:
    """Tests for polygon geometry validation."""

    def test_valid_polygon_simple_rectangle(self):
        """Valid 4-vertex rectangle should be accepted."""
        geom = PolygonGeometry(
            type="Polygon",
            coordinates=[[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
        )
        assert len(geom.coordinates[0]) == 5  # 4 vertices + closure

    def test_valid_polygon_triangle(self):
        """Valid 3-vertex triangle should be accepted (minimum)."""
        geom = PolygonGeometry(
            type="Polygon",
            coordinates=[[(0, 0), (10, 0), (5, 10), (0, 0)]],
        )
        assert len(geom.coordinates[0]) == 4

    def test_polygon_not_closed_rejected(self):
        """Polygon with non-matching start/end coordinates should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PolygonGeometry(
                type="Polygon",
                coordinates=[[(0, 0), (10, 0), (10, 10), (0, 10)]],  # Not closed
            )
        assert "must be closed" in str(exc_info.value)

    def test_polygon_too_few_vertices_rejected(self):
        """Polygon with < 4 coordinates should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PolygonGeometry(
                type="Polygon",
                coordinates=[[(0, 0), (10, 0), (0, 0)]],  # Only 3 points, needs closure
            )
        assert "at least 4 coordinates" in str(exc_info.value)

    def test_polygon_with_hole_rejected(self):
        """Polygon with hole (multiple rings) should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PolygonGeometry(
                type="Polygon",
                coordinates=[
                    [(0, 0), (20, 0), (20, 20), (0, 20), (0, 0)],  # Exterior
                    [(5, 5), (15, 5), (15, 15), (5, 15), (5, 5)],  # Interior hole
                ],
            )
        assert "single exterior ring" in str(exc_info.value)

    def test_empty_coordinates_rejected(self):
        """Empty coordinates array should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PolygonGeometry(type="Polygon", coordinates=[])
        assert "single exterior ring" in str(exc_info.value)


# Coordinate validation tests
class TestCoordinateValidation:
    """Tests for coordinate pair validation."""

    def test_valid_coordinate_pair(self):
        """Valid [lon, lat] pair should be accepted."""
        geom = PolygonGeometry(
            type="Polygon",
            coordinates=[[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 0.0)]],
        )
        assert geom.coordinates[0][0] == [0.0, 0.0]

    def test_coordinate_too_few_values_rejected(self):
        """Coordinate with only 1 value should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PolygonGeometry(
                type="Polygon",
                coordinates=[[(0,), (10, 0), (10, 10), (0, 0)]],
            )
        assert "at least 2 items" in str(exc_info.value)

    def test_coordinate_too_many_values_rejected(self):
        """Coordinate with > 2 values should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PolygonGeometry(
                type="Polygon",
                coordinates=[[(0, 0, 0), (10, 0), (10, 10), (0, 0)]],
            )
        assert "at most 2 items" in str(exc_info.value)


# GeoJSON Feature validation tests
class TestGeoJSONFeatureValidation:
    """Tests for GeoJSON Feature validation."""

    def test_valid_feature(self):
        """Valid feature with all required fields should be accepted."""
        feature = GeoJSONFeature(
            type="Feature",
            id="building1",
            properties=BuildingProperties(height=10, elevation=0),
            geometry=PolygonGeometry(
                type="Polygon",
                coordinates=[[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
            ),
        )
        assert feature.id == "building1"

    def test_feature_missing_id_rejected(self):
        """Feature without id should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            GeoJSONFeature(
                type="Feature",
                properties=BuildingProperties(height=10, elevation=0),
                geometry=PolygonGeometry(
                    type="Polygon",
                    coordinates=[[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                ),
            )
        assert "id" in str(exc_info.value)

    def test_feature_invalid_height_rejected(self):
        """Feature with invalid height should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            GeoJSONFeature(
                type="Feature",
                id="building1",
                properties=BuildingProperties(height=0, elevation=0),  # Invalid
                geometry=PolygonGeometry(
                    type="Polygon",
                    coordinates=[[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                ),
            )
        assert "greater than 0" in str(exc_info.value)

    def test_feature_invalid_polygon_rejected(self):
        """Feature with invalid polygon should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            GeoJSONFeature(
                type="Feature",
                id="building1",
                properties=BuildingProperties(height=10, elevation=0),
                geometry=PolygonGeometry(
                    type="Polygon",
                    coordinates=[[(0, 0), (10, 0), (10, 10), (0, 10)]],
                ),
            )
        assert "must be closed" in str(exc_info.value)


# FeatureCollection validation tests
class TestFeatureCollectionValidation:
    """Tests for GeoJSON FeatureCollection validation."""

    def test_valid_feature_collection(self):
        """Valid FeatureCollection with features should be accepted."""
        fc = GeoJSONFeatureCollection(
            type="FeatureCollection",
            features=[
                GeoJSONFeature(
                    type="Feature",
                    id="building1",
                    properties=BuildingProperties(height=10, elevation=0),
                    geometry=PolygonGeometry(
                        type="Polygon",
                        coordinates=[[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                    ),
                ),
                GeoJSONFeature(
                    type="Feature",
                    id="building2",
                    properties=BuildingProperties(height=15, elevation=5),
                    geometry=PolygonGeometry(
                        type="Polygon",
                        coordinates=[
                            [(20, 20), (30, 20), (30, 30), (20, 30), (20, 20)]
                        ],
                    ),
                ),
            ],
        )
        assert len(fc.features) == 2

    def test_empty_feature_collection_rejected(self):
        """FeatureCollection with no features should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            GeoJSONFeatureCollection(type="FeatureCollection", features=[])
        assert "at least one feature" in str(exc_info.value)


# ClashDetectionRequest validation tests
class TestClashDetectionRequestValidation:
    """Tests for ClashDetectionRequest validation (inherits FeatureCollection)."""

    def test_valid_clash_detection_request(self):
        """Valid request with features should be accepted."""
        request = ClashDetectionRequest(
            type="FeatureCollection",
            features=[
                GeoJSONFeature(
                    type="Feature",
                    id="building1",
                    properties=BuildingProperties(height=10, elevation=0),
                    geometry=PolygonGeometry(
                        type="Polygon",
                        coordinates=[[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                    ),
                ),
            ],
        )
        assert len(request.features) == 1

    def test_request_empty_features_rejected(self):
        """Request with empty features should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ClashDetectionRequest(type="FeatureCollection", features=[])
        assert "at least one feature" in str(exc_info.value)

    def test_request_invalid_feature_rejected(self):
        """Request with invalid feature should be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ClashDetectionRequest(
                type="FeatureCollection",
                features=[
                    GeoJSONFeature(
                        type="Feature",
                        id="building1",
                        properties=BuildingProperties(
                            height=-5, elevation=0
                        ),  # Invalid
                        geometry=PolygonGeometry(
                            type="Polygon",
                            coordinates=[[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                        ),
                    ),
                ],
            )
        assert "greater than 0" in str(exc_info.value)
