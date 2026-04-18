import pytest
from app.algorithms.clash_detector import detect_clashes

# Sample input matching input-sample1.json format
SAMPLE_BUILDINGS = [
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [0, 0], [10, 0], [10, 10], [0, 10], [0, 0]
            ]]
        },
        "properties": {
            "id": "building1",
            "height": 10,
            "elevation": 0
        }
    },
    {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [5, 5], [15, 5], [15, 15], [5, 15], [5, 5]
            ]]
        },
        "properties": {
            "id": "building2",
            "height": 10,
            "elevation": 0
        }
    }
]

def test_detect_clashes_returns_overlap():
    """Test that overlapping buildings produce clash features."""
    result = detect_clashes(SAMPLE_BUILDINGS)
    
    assert result['type'] == 'FeatureCollection'
    assert len(result['features']) > 0
    
    # Check properties
    feature = result['features'][0]
    assert 'buildingIds' in feature['properties']
    assert 'height' in feature['properties']
    assert 'elevation' in feature['properties']

def test_no_overlap():
    """Test that non-overlapping buildings return empty result."""
    non_overlapping = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]
            },
            "properties": {"id": "b1", "height": 10, "elevation": 0}
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[20, 20], [30, 20], [30, 30], [20, 30], [20, 20]]]
            },
            "properties": {"id": "b2", "height": 10, "elevation": 0}
        }
    ]
    
    result = detect_clashes(non_overlapping)
    
    assert result['type'] == 'FeatureCollection'
    assert len(result['features']) == 0
