export const sampleInputOne = {
    type: "FeatureCollection",
    features: [
        {
            type: "Feature",
            id: "building_0",
            properties: { height: 4, elevation: 0 },
            geometry: {
                type: "Polygon",
                coordinates: [[[20, 0], [20, 60], [0, 60], [0, 0], [20, 0]]]
            }
        },
        {
            type: "Feature",
            id: "building_1",
            properties: { height: 4, elevation: 2 },
            geometry: {
                type: "Polygon",
                coordinates: [[[60, 60], [0, 60], [0, 40], [60, 40], [60, 60]]]
            }
        },
        {
            type: "Feature",
            id: "building_2",
            properties: { height: 4, elevation: 4 },
            geometry: {
                type: "Polygon",
                coordinates: [[[60, 0], [60, 60], [40, 60], [40, 0], [60, 0]]]
            }
        },
        {
            type: "Feature",
            id: "building_3",
            properties: { height: 4, elevation: 6 },
            geometry: {
                type: "Polygon",
                coordinates: [[[60, 20], [0, 20], [0, 0], [60, 0], [60, 20]]]
            }
        }
    ]
};

export const sampleInputTwo = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "id": "building_0",
      "properties": {
        "height": 4,
        "elevation": 0
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              20,
              0
            ],
            [
              20,
              40
            ],
            [
              40,
              40
            ],
            [
              40,
              0
            ],
            [
              20,
              0
            ]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "id": "building_1",
      "properties": {
        "height": 4,
        "elevation": 0
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              0,
              20
            ],
            [
              0,
              40
            ],
            [
              40,
              40
            ],
            [
              40,
              20
            ],
            [
              0,
              20
            ]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "id": "building_2",
      "properties": {
        "height": 4,
        "elevation": 0
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              20,
              20
            ],
            [
              20,
              60
            ],
            [
              40,
              60
            ],
            [
              40,
              20
            ],
            [
              20,
              20
            ]
          ]
        ]
      }
    }
  ]
}

export const sampleOutputOne = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "elevation": 2,
        "height": 2,
        "buildings": ["building_0", "building_1"]
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [0, 40],
            [20, 40],
            [20, 60],
            [0, 60],
            [0, 40]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "elevation": 4,
        "height": 2,
        "buildings": ["building_1", "building_2"]
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [40, 40],
            [60, 40],
            [60, 60],
            [40, 60],
            [40, 40]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "elevation": 6,
        "height": 2,
        "buildings": ["building_2", "building_3"]
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [40, 0],
            [60, 0],
            [60, 20],
            [40, 20],
            [40, 0]
          ]
        ]
      }
    }
  ]
};

export const sampleOutputTwo = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "elevation": 0,
        "height": 4,
        "buildings": ["building_0", "building_1"]
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [20, 20],
            [40, 20],
            [40, 40],
            [20, 40],
            [20, 20]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "elevation": 0,
        "height": 4,
        "buildings": ["building_0", "building_2"]
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [20, 20],
            [40, 20],
            [40, 40],
            [20, 40],
            [20, 20]
          ]
        ]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "elevation": 0,
        "height": 4,
        "buildings": ["building_1", "building_2"]
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [20, 20],
            [40, 20],
            [40, 40],
            [20, 40],
            [20, 20]
          ]
        ]
      }
    }
  ]
};

export const samples = {
    sampleInputOne,
    sampleInputTwo,
    sampleOutputOne,
    sampleOutputTwo
};
