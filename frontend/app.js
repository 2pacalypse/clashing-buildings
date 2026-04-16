import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { sampleInputOne } from './data.js';

// Color palette for buildings
const buildingColors = [
    0x4a90d9, 0x50c878, 0xf4a460, 0x9370db, 0x20b2aa,
    0xff6b6b, 0x4ecdc4, 0xffe66d, 0x95e1d3, 0xf38181
];

// Global state
let scene, camera, renderer, controls;
let buildingMeshes = [];
let overlapMeshes = [];
let raycaster = new THREE.Raycaster();
let mouse = new THREE.Vector2();

// Initialize Three.js
function init() {
    const canvas = document.getElementById('three-canvas');
    
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);
    
    camera = new THREE.PerspectiveCamera(60, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
    camera.position.set(50, 40, 50);
    
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    
    // Lighting
    scene.add(new THREE.AmbientLight(0xffffff, 0.6));
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(50, 100, 50);
    scene.add(directionalLight);
    
    // Grid and axes
    scene.add(new THREE.GridHelper(100, 20, 0x444444, 0x222222));
    scene.add(new THREE.AxesHelper(10));
    
    // Event listeners
    window.addEventListener('resize', onResize);
    canvas.addEventListener('mousemove', onMouseMove);
    
    // Start animation loop
    animate();
    
    // Load default sample
    loadSample();
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

function onResize() {
    const canvas = document.getElementById('three-canvas');
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
}

function onMouseMove(event) {
    const canvas = document.getElementById('three-canvas');
    const rect = canvas.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    
    raycaster.setFromCamera(mouse, camera);
    const allMeshes = [...buildingMeshes, ...overlapMeshes];
    const intersects = raycaster.intersectObjects(allMeshes);
    
    const overlay = document.getElementById('overlay-info');
    if (intersects.length > 0) {
        const data = intersects[0].object.userData;
        if (data.type === 'building') {
            const f = data.feature;
            overlay.innerHTML = `<strong>${f.id}</strong><br>Height: ${f.properties.height}m<br>Elevation: ${f.properties.elevation}m`;
            overlay.style.display = 'block';
        } else if (data.type === 'overlap') {
            const f = data.feature;
            overlay.innerHTML = `<strong>Overlap</strong><br>Buildings: ${f.properties.buildingIds.join(', ')}<br>Height: ${f.properties.height}m<br>Elevation: ${f.properties.elevation}m`;
            overlay.style.display = 'block';
        }
    } else {
        overlay.style.display = 'none';
    }
}

function createBuildingMesh(feature, index = 0) {
    const coords = feature.geometry.coordinates[0];
    
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    
    coords.forEach(c => {
        minX = Math.min(minX, c[0]);
        maxX = Math.max(maxX, c[0]);
        minY = Math.min(minY, c[1]);
        maxY = Math.max(maxY, c[1]);
    });
    
    const width = maxX - minX;
    const depth = maxY - minY;
    const height = feature.properties.height;
    const elevation = feature.properties.elevation;
    
    const geometry = new THREE.BoxGeometry(width, height, depth);
    const color = buildingColors[index % buildingColors.length];
    const material = new THREE.MeshPhongMaterial({
        color: color,
        transparent: true,
        opacity: 0.7,
        side: THREE.DoubleSide
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set((minX + maxX) / 2, elevation + height / 2, (minY + maxY) / 2);
    mesh.userData = { type: 'building', feature, color };
    
    const edges = new THREE.EdgesGeometry(geometry);
    const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: color + 0x303030 }));
    mesh.add(line);
    
    return mesh;
}

function createOverlapMesh(overlapFeature) {
    const coords = overlapFeature.geometry.coordinates[0];
    
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    
    coords.forEach(c => {
        minX = Math.min(minX, c[0]);
        maxX = Math.max(maxX, c[0]);
        minY = Math.min(minY, c[1]);
        maxY = Math.max(maxY, c[1]);
    });
    
    const width = maxX - minX;
    const depth = maxY - minY;
    const height = overlapFeature.properties.height;
    const elevation = overlapFeature.properties.elevation;
    
    const geometry = new THREE.BoxGeometry(width, height, depth);
    const material = new THREE.MeshPhongMaterial({
        color: 0xe94560,
        transparent: true,
        opacity: 0.85,
        side: THREE.DoubleSide
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set((minX + maxX) / 2, elevation + height / 2, (minY + maxY) / 2);
    mesh.userData = { type: 'overlap', feature: overlapFeature };
    
    const edges = new THREE.EdgesGeometry(geometry);
    const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0xff8888 }));
    mesh.add(line);
    
    return mesh;
}

function clearScene() {
    buildingMeshes.forEach(m => scene.remove(m));
    overlapMeshes.forEach(m => scene.remove(m));
    buildingMeshes = [];
    overlapMeshes = [];
}

function renderGeoJSON(geojson, overlaps = null) {
    clearScene();
    
    geojson.features.forEach((feature, index) => {
        const mesh = createBuildingMesh(feature, index);
        scene.add(mesh);
        buildingMeshes.push(mesh);
    });
    
    if (overlaps && overlaps.features && overlaps.features.length > 0) {
        overlaps.features.forEach(feature => {
            const mesh = createOverlapMesh(feature);
            scene.add(mesh);
            overlapMeshes.push(mesh);
        });
    }
    
    // Fit camera
    if (buildingMeshes.length > 0) {
        const box = new THREE.Box3().setFromObject(buildingMeshes[0]);
        buildingMeshes.forEach(m => box.expandByObject(m));
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        
        camera.position.set(center.x + maxDim, maxDim * 0.8, center.z + maxDim);
        controls.target.copy(center);
    }
    
    // Update legend
    const legendHtml = geojson.features.map((f, i) => {
        const color = '#' + buildingColors[i % buildingColors.length].toString(16).padStart(6, '0');
        return `<div class="legend-item">
            <div class="legend-color" style="background: ${color};"></div>
            <span>${f.id} (${f.properties.height}m @ ${f.properties.elevation}m)</span>
        </div>`;
    }).join('');
    
    document.getElementById('legend').innerHTML = legendHtml + 
        `<div class="legend-item" style="margin-top:10px;">
            <div class="legend-color" style="background: #e94560;"></div>
            <span>Overlaps</span>
        </div>`;
}

function validateGeoJSON(geojson) {
    if (!geojson || typeof geojson !== 'object') return 'Invalid JSON format';
    if (geojson.type !== 'FeatureCollection') return 'Root must be a FeatureCollection';
    if (!Array.isArray(geojson.features) || geojson.features.length === 0) return 'FeatureCollection must have at least one feature';
    
    for (let i = 0; i < geojson.features.length; i++) {
        const f = geojson.features[i];
        if (f.type !== 'Feature') return `Feature ${i}: must have type "Feature"`;
        if (!f.id) return `Feature ${i}: must have an "id" field`;
        if (!f.geometry || f.geometry.type !== 'Polygon') return `Feature ${i}: geometry must be a Polygon`;
        if (!f.properties || f.properties.height == null || f.properties.elevation == null) {
            return `Feature ${i}: properties must include height and elevation`;
        }
    }
    return null;
}

function visualizeInput() {
    document.getElementById('error').style.display = 'none';
    const input = document.getElementById('geojsonInput').value.trim();
    
    if (!input) {
        showError('Please enter a GeoJSON');
        return;
    }
    
    let geojson;
    try {
        geojson = JSON.parse(input);
    } catch (e) {
        showError('Invalid JSON: ' + e.message);
        return;
    }
    
    const error = validateGeoJSON(geojson);
    if (error) {
        showError(error);
        return;
    }
    
    document.querySelector('.sample-btn').classList.add('active');
    renderGeoJSON(geojson);
}

function loadSample() {
    document.getElementById('geojsonInput').value = JSON.stringify(sampleInputOne, null, 2);
    document.querySelector('.sample-btn').classList.add('active');
    renderGeoJSON(sampleInputOne);
}

function clearInput() {
    document.getElementById('geojsonInput').value = '';
    document.getElementById('error').style.display = 'none';
    document.querySelector('.sample-btn').classList.remove('active');
    clearScene();
    document.getElementById('legend').innerHTML = '';
}

function showError(msg) {
    const el = document.getElementById('error');
    el.textContent = msg;
    el.style.display = 'block';
}

function resetCamera() {
    if (buildingMeshes.length > 0) {
        const box = new THREE.Box3().setFromObject(buildingMeshes[0]);
        buildingMeshes.forEach(m => box.expandByObject(m));
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        
        camera.position.set(center.x + maxDim, maxDim * 0.8, center.z + maxDim);
        controls.target.copy(center);
    }
}

function topDownView() {
    if (buildingMeshes.length > 0) {
        const box = new THREE.Box3().setFromObject(buildingMeshes[0]);
        buildingMeshes.forEach(m => box.expandByObject(m));
        const center = box.getCenter(new THREE.Vector3());
        
        camera.position.set(center.x, 80, center.z);
        controls.target.copy(center);
    }
}

function sideView() {
    if (buildingMeshes.length > 0) {
        const box = new THREE.Box3().setFromObject(buildingMeshes[0]);
        buildingMeshes.forEach(m => box.expandByObject(m));
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        camera.position.set(center.x + size.x * 1.5, 5, center.z);
        controls.target.copy(center);
    }
}

// Expose functions globally
window.visualizeInput = visualizeInput;
window.loadSample = loadSample;
window.clearInput = clearInput;
window.resetCamera = resetCamera;
window.topDownView = topDownView;
window.sideView = sideView;

// Initialize on load
init();
