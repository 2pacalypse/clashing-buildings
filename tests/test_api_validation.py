"""
API endpoint validation tests - Integration tests for HTTP error responses.

Tests verify that the /api/v1/detect-clashes endpoint returns appropriate
HTTP status codes and error response formats for invalid inputs.
"""

import pytest


# Height validation error tests
def test_api_negative_height_returns_422(client):
    """POST with negative height should return 422 Unprocessable Entity."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": -5, "elevation": 0},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422
    response_body = response.json()
    assert response_body["code"] == "VALIDATION_ERROR"
    assert response_body["message"] == "Request validation failed"
    assert "errors" in response_body["details"]


def test_api_zero_height_returns_422(client):
    """POST with zero height should return 422 Unprocessable Entity."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": 0, "elevation": 0},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


# Elevation validation error tests
def test_api_negative_elevation_returns_422(client):
    """POST with negative elevation should return 422 Unprocessable Entity."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": 10, "elevation": -5},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


# Polygon geometry validation error tests
def test_api_polygon_not_closed_returns_422(client):
    """POST with unclosed polygon should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": 10, "elevation": 0},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [(0, 0), (10, 0), (10, 10), (0, 10)]
                        ],  # Not closed
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


def test_api_polygon_too_few_vertices_returns_422(client):
    """POST with polygon having < 4 coordinates should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": 10, "elevation": 0},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0), (10, 0), (0, 0)]],  # Only 3 points
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


def test_api_polygon_with_hole_returns_422(client):
    """POST with polygon containing hole (multiple rings) should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": 10, "elevation": 0},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [(0, 0), (20, 0), (20, 20), (0, 20), (0, 0)],  # Exterior
                            [
                                (5, 5),
                                (15, 5),
                                (15, 15),
                                (5, 15),
                                (5, 5),
                            ],  # Interior hole
                        ],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


# Coordinate validation error tests
def test_api_coordinate_too_few_values_returns_422(client):
    """POST with coordinate having < 2 values should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": 10, "elevation": 0},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0,), (10, 0), (10, 10), (0, 0)]],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


def test_api_coordinate_too_many_values_returns_422(client):
    """POST with coordinate having > 2 values should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": 10, "elevation": 0},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0, 0), (10, 0), (10, 10), (0, 0)]],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


# Feature collection validation error tests
def test_api_empty_feature_collection_returns_422(client):
    """POST with empty features array should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={"type": "FeatureCollection", "features": []},
    )
    assert response.status_code == 422


def test_api_missing_feature_id_returns_422(client):
    """POST with feature missing 'id' field should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    # Missing 'id' field
                    "properties": {"height": 10, "elevation": 0},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


def test_api_missing_properties_returns_422(client):
    """POST with feature missing 'properties' field should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    # Missing 'properties' field
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


def test_api_missing_height_returns_422(client):
    """POST with properties missing 'height' should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"elevation": 0},  # Missing 'height'
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


def test_api_missing_elevation_returns_422(client):
    """POST with properties missing 'elevation' should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": 10},  # Missing 'elevation'
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


def test_api_missing_geometry_returns_422(client):
    """POST with feature missing 'geometry' should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": 10, "elevation": 0},
                    # Missing 'geometry' field
                },
            ],
        },
    )
    assert response.status_code == 422


# Invalid type/format tests
def test_api_invalid_feature_type_returns_422(client):
    """POST with wrong Feature type should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "InvalidType",  # Should be "Feature"
                    "id": "building1",
                    "properties": {"height": 10, "elevation": 0},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


def test_api_invalid_geometry_type_returns_422(client):
    """POST with unsupported geometry type should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": 10, "elevation": 0},
                    "geometry": {
                        "type": "Point",  # Should be "Polygon"
                        "coordinates": [0, 0],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


# Non-JSON body tests
def test_api_non_json_body_returns_400(client):
    """POST with non-JSON body should return 400 Bad Request."""
    response = client.post(
        "/api/v1/detect-clashes",
        data="not json",
        headers={"Content-Type": "text/plain"},
    )
    assert response.status_code in [400, 422]


# Multiple features with mixed validity
def test_api_multiple_features_one_invalid_returns_422(client):
    """POST with multiple features where one is invalid should return 422."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": 10, "elevation": 0},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                    },
                },
                {
                    "type": "Feature",
                    "id": "building2",
                    "properties": {"height": -5, "elevation": 0},  # Invalid height
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [(20, 20), (30, 20), (30, 30), (20, 30), (20, 20)]
                        ],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422


# Error response format tests
def test_api_error_response_has_structured_fields(client):
    """Error response should include structured code, message, and details fields."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "building1",
                    "properties": {"height": 0, "elevation": 0},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]],
                    },
                },
            ],
        },
    )
    assert response.status_code == 422
    response_body = response.json()
    assert response_body["code"] == "VALIDATION_ERROR"
    assert response_body["message"] == "Request validation failed"
    assert "errors" in response_body["details"]


def test_api_error_response_is_json(client):
    """Error response should be valid JSON."""
    response = client.post(
        "/api/v1/detect-clashes",
        json={"type": "FeatureCollection", "features": []},
    )
    assert response.status_code == 422
    # Should not raise JSONDecodeError
    response_body = response.json()
    assert isinstance(response_body, dict)
