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

export const test100Buildings = {
  type: "FeatureCollection",
  features: Array.from({ length: 100 }, (_, i) => {
    let x, y;
    if (i < 2) {
      x = i * 5;
      y = 0;
    } else {
      x = ((i - 2) % 14) * 20;
      y = 20 + Math.floor((i - 2) / 14) * 20;
    }
    return {
      type: "Feature",
      id: `building_${i}`,
      properties: { height: 4, elevation: 0 },
      geometry: {
        type: "Polygon",
        coordinates: [[[x, y], [x + 10, y], [x + 10, y + 10], [x, y + 10], [x, y]]]
      }
    };
  })
};

export const test200Buildings = {
  type: "FeatureCollection",
  features: Array.from({ length: 200 }, (_, i) => {
    let x, y;
    if (i < 2) {
      x = i * 5;
      y = 0;
    } else {
      x = ((i - 2) % 20) * 20;
      y = 20 + Math.floor((i - 2) / 20) * 20;
    }
    return {
      type: "Feature",
      id: `building_${i}`,
      properties: { height: 4, elevation: 0 },
      geometry: {
        type: "Polygon",
        coordinates: [[[x, y], [x + 10, y], [x + 10, y + 10], [x, y + 10], [x, y]]]
      }
    };
  })
};

export const test300Buildings = {
  type: "FeatureCollection",
  features: Array.from({ length: 300 }, (_, i) => {
    let x, y;
    if (i < 2) {
      x = i * 5;
      y = 0;
    } else {
      x = ((i - 2) % 24) * 20;
      y = 20 + Math.floor((i - 2) / 24) * 20;
    }
    return {
      type: "Feature",
      id: `building_${i}`,
      properties: { height: 4, elevation: 0 },
      geometry: {
        type: "Polygon",
        coordinates: [[[x, y], [x + 10, y], [x + 10, y + 10], [x, y + 10], [x, y]]]
      }
    };
  })
};

export const test400Buildings = {
  type: "FeatureCollection",
  features: Array.from({ length: 400 }, (_, i) => {
    let x, y;
    if (i < 2) {
      x = i * 5;
      y = 0;
    } else {
      x = ((i - 2) % 28) * 20;
      y = 20 + Math.floor((i - 2) / 28) * 20;
    }
    return {
      type: "Feature",
      id: `building_${i}`,
      properties: { height: 4, elevation: 0 },
      geometry: {
        type: "Polygon",
        coordinates: [[[x, y], [x + 10, y], [x + 10, y + 10], [x, y + 10], [x, y]]]
      }
    };
  })
};

export const test500Buildings = {
  type: "FeatureCollection",
  features: Array.from({ length: 500 }, (_, i) => {
    let x, y;
    if (i < 2) {
      x = i * 5;
      y = 0;
    } else {
      x = ((i - 2) % 32) * 20;
      y = 20 + Math.floor((i - 2) / 32) * 20;
    }
    return {
      type: "Feature",
      id: `building_${i}`,
      properties: { height: 4, elevation: 0 },
      geometry: {
        type: "Polygon",
        coordinates: [[[x, y], [x + 10, y], [x + 10, y + 10], [x, y + 10], [x, y]]]
      }
    };
  })
};

export const test600Buildings = {
  type: "FeatureCollection",
  features: Array.from({ length: 600 }, (_, i) => {
    let x, y;
    if (i < 2) {
      x = i * 5;
      y = 0;
    } else {
      x = ((i - 2) % 35) * 20;
      y = 20 + Math.floor((i - 2) / 35) * 20;
    }
    return {
      type: "Feature",
      id: `building_${i}`,
      properties: { height: 4, elevation: 0 },
      geometry: {
        type: "Polygon",
        coordinates: [[[x, y], [x + 10, y], [x + 10, y + 10], [x, y + 10], [x, y]]]
      }
    };
  })
};

export const samples = {
    sampleInputOne,
    sampleInputTwo,
    sampleOutputOne,
    sampleOutputTwo,
    test100Buildings,
    test200Buildings,
    test300Buildings,
    test400Buildings,
    test500Buildings,
    test600Buildings
};
