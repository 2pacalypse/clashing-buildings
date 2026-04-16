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
    type: "FeatureCollection",
    features: [
        {
            type: "Feature",
            id: "tower_a",
            properties: { height: 30, elevation: 0 },
            geometry: {
                type: "Polygon",
                coordinates: [[[10, 10], [10, 30], [30, 30], [30, 10], [10, 10]]]
            }
        },
        {
            type: "Feature",
            id: "tower_b",
            properties: { height: 25, elevation: 0 },
            geometry: {
                type: "Polygon",
                coordinates: [[[25, 25], [25, 45], [45, 45], [45, 25], [25, 25]]]
            }
        },
        {
            type: "Feature",
            id: "tower_c",
            properties: { height: 20, elevation: 0 },
            geometry: {
                type: "Polygon",
                coordinates: [[[0, 40], [0, 60], [20, 60], [20, 40], [0, 40]]]
            }
        }
    ]
};

export const sampleInputThree = {
    type: "FeatureCollection",
    features: [
        {
            type: "Feature",
            id: "low_1",
            properties: { height: 5, elevation: 0 },
            geometry: {
                type: "Polygon",
                coordinates: [[[0, 0], [0, 20], [20, 20], [20, 0], [0, 0]]]
            }
        },
        {
            type: "Feature",
            id: "low_2",
            properties: { height: 5, elevation: 0 },
            geometry: {
                type: "Polygon",
                coordinates: [[[15, 15], [15, 35], [35, 35], [35, 15], [15, 15]]]
            }
        },
        {
            type: "Feature",
            id: "mid_1",
            properties: { height: 10, elevation: 5 },
            geometry: {
                type: "Polygon",
                coordinates: [[[5, 5], [5, 15], [15, 15], [15, 5], [5, 5]]]
            }
        },
        {
            type: "Feature",
            id: "mid_2",
            properties: { height: 10, elevation: 5 },
            geometry: {
                type: "Polygon",
                coordinates: [[[20, 20], [20, 30], [30, 30], [30, 20], [20, 20]]]
            }
        }
    ]
};

export const samples = {
    sampleInputOne,
    sampleInputTwo,
    sampleInputThree
};
