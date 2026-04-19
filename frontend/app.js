import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { sampleInputOne, sampleInputTwo, samples } from './data.js';

// Copy icon (emoji)
const copyIconSvg = '📋';

// Color palette for buildings (light background friendly)
const buildingColors = [
    0x3498db, 0x2ecc71, 0xe67e22, 0x9b59b6, 0x1abc9c,
    0xe74c3c, 0x34495e, 0xf39c12, 0x16a085, 0x8e44ad
];

// Color for intersections (red)
const intersectionColor = 0xe74c3c;
const intersectionEdgeColor = 0xc0392b;

// Global state
let scene, camera, renderer, controls;
let buildingMeshes = [];
let overlapMeshes = [];
let raycaster = new THREE.Raycaster();
let mouse = new THREE.Vector2();
let selectedSamples = new Set();

// Initialize Three.js
function init() {
    const canvas = document.getElementById('three-canvas');
    
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xe8e8e8);
    
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
    scene.add(new THREE.GridHelper(100, 20, 0xbbbbbb, 0xdddddd));
    scene.add(new THREE.AxesHelper(10));
    
    // Event listeners
    window.addEventListener('resize', onResize);
    canvas.addEventListener('mousemove', onMouseMove);
    
    // Start animation loop
    animate();

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
        if (data.type === 'building' || data.type === 'output') {
            const f = data.feature;
            const label = data.type === 'output' ? 'Intersection' : f.id;
            overlay.innerHTML = `<strong>${label}</strong><br>Height: ${f.properties.height}m<br>Elevation: ${f.properties.elevation}m`;
            overlay.style.display = 'block';
        } else if (data.type === 'overlap') {
            const f = data.feature;
            overlay.innerHTML = `<strong>Overlap</strong><br>Buildings: ${f.properties.buildings.join(', ')}<br>Height: ${f.properties.height}m<br>Elevation: ${f.properties.elevation}m`;
            overlay.style.display = 'block';
        }
    } else {
        overlay.style.display = 'none';
    }
}

function createBuildingMesh(feature, index = 0, isOutput = false) {
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
    
    let color, edgeColor, opacity;
    
    if (isOutput) {
        color = intersectionColor;
        edgeColor = intersectionEdgeColor;
        opacity = 0.9;
    } else {
        color = buildingColors[index % buildingColors.length];
        edgeColor = color - 0x202020;
        opacity = 0.5;
    }
    
    const material = new THREE.MeshPhongMaterial({
        color: color,
        transparent: true,
        opacity: opacity,
        side: THREE.DoubleSide
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    
    mesh.position.set((minX + maxX) / 2, elevation + height / 2, (minY + maxY) / 2);
    mesh.userData = { type: isOutput ? 'output' : 'building', feature, color };
    
    const edges = new THREE.EdgesGeometry(geometry);
    const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: edgeColor }));
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
        const labelText = f.id;
        const fullLabel = `${labelText} (${f.properties.height}m @ ${f.properties.elevation}m)`;
        const shortLabel = labelText.slice(0, 3);
        return `<div class="legend-item">
            <div class="legend-color" style="background: ${color};"></div>
            <span class="legend-label" title="${fullLabel}">${shortLabel}</span>
        </div>`;
    }).join('');

    const overlapsShort = 'Ove';
    const overlapsFull = 'Overlaps';
    document.getElementById('legend').innerHTML = legendHtml + 
        `<div class="legend-item" style="margin-top:10px;">
            <div class="legend-color" style="background: #e94560;"></div>
            <span class="legend-label" title="${overlapsFull}">${overlapsShort}</span>
        </div>`;
}

function loadSample(sampleKey) {
    const sample = samples[sampleKey] || sampleInputOne;
    
    // Toggle selection
    if (selectedSamples.has(sampleKey)) {
        selectedSamples.delete(sampleKey);
        document.querySelector(`[data-sample="${sampleKey}"]`).classList.remove('active');
    } else {
        selectedSamples.add(sampleKey);
        document.querySelector(`[data-sample="${sampleKey}"]`).classList.add('active');
    }
    
    // Render all selected samples
    renderAllSelectedSamples();
}

function renderAllSelectedSamples() {
    clearScene();
    
    if (selectedSamples.size === 0) {
        document.getElementById('legend').innerHTML = '';
        return;
    }
    
    let colorIndex = 0;
    
    selectedSamples.forEach(key => {
        const sample = samples[key];
        const isOutput = key.toLowerCase().includes('output');
        
        if (sample && sample.features) {
            sample.features.forEach((f, idx) => {
                const mesh = createBuildingMesh(f, colorIndex++, isOutput);
                scene.add(mesh);
                buildingMeshes.push(mesh);
            });
        }
    });
    
    // Update legend
    updateLegend();
}

function updateLegend() {
    let legendHtml = '';
    let colorIndex = 0;
    
    selectedSamples.forEach(key => {
        const sample = samples[key];
        const isOutput = key.toLowerCase().includes('output');
        
        if (sample && sample.features) {
            sample.features.forEach(f => {
                const label = isOutput ? 'Intersection' : f.id;
                let bgColor, borderColor;
                
                if (isOutput) {
                    bgColor = '#e74c3c';
                    borderColor = '#c0392b';
                } else {
                    const color = buildingColors[colorIndex % buildingColors.length];
                    bgColor = '#' + color.toString(16).padStart(6, '0');
                    borderColor = '#' + (color - 0x202020).toString(16).padStart(6, '0');
                    colorIndex++;
                }
                
                const labelText = label;
                const fullLabel = `${labelText} (${f.properties.height}m @ ${f.properties.elevation}m)`;
                const shortLabel = labelText.slice(0,3);
                legendHtml += `<div class="legend-item">
                    <div class="legend-color" style="background: ${bgColor}; border: 1px solid ${borderColor};"></div>
                    <span class="legend-label" title="${fullLabel}">${shortLabel}</span>
                </div>`;
            });
        }
    });
    
    document.getElementById('legend').innerHTML = legendHtml;
}

function clearInput() {
    document.querySelectorAll('.sample-btn').forEach(btn => btn.classList.remove('active'));
    selectedSamples.clear();
    clearScene();
    document.getElementById('legend').innerHTML = '';
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
window.loadSample = loadSample;
window.clearInput = clearInput;
window.resetCamera = resetCamera;
window.topDownView = topDownView;
window.sideView = sideView;

// Accept JSON pasted into the textarea and render it

window.sendInputFromForm = async function() {
    const ta = document.getElementById('input-json');
    if (!ta) return;
    const statusEl = document.getElementById('input-status');
    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) { sendBtn.disabled = true; sendBtn.textContent = 'Sending...'; }
    if (statusEl) { statusEl.textContent = ''; }
    let parsed;
    try {
        parsed = JSON.parse(ta.value);
        if (!parsed || !parsed.features) throw new Error('Not a FeatureCollection');
    } catch (err) {
        if (sendBtn) { sendBtn.disabled = false; sendBtn.textContent = 'Send'; }
        return;
    }

    // Determine next input sample index (count existing sample-input buttons)
    const existingInputBtns = Array.from(document.querySelectorAll('.sample-btn')).filter(b => {
        const ds = b.dataset && b.dataset.sample ? b.dataset.sample.toLowerCase() : '';
        return ds.includes('input');
    });
    const nextIndex = existingInputBtns.length + 1;
    const key = 'sampleInput' + nextIndex;

    // Register new sample in the samples object so loadSample can find it
    // Declare these here so they are available after the POST response
    let outKey;
    let inBtn, outBtn, row;
    try {
        samples[key] = parsed;
        outKey = 'sampleOutput' + nextIndex;
        // create a dummy empty FeatureCollection for the paired output
        samples[outKey] = { type: 'FeatureCollection', features: [] };

        // Create paired buttons and insert into the Sample Inputs section
        const section = document.getElementById('sample-section');
        if (section) {
            row = document.createElement('div');
            row.className = 'sample-row';

            // LEFT: input item (button + copy field stacked)
            const leftItem = document.createElement('div');
            leftItem.className = 'sample-item';

            inBtn = document.createElement('button');
            inBtn.className = 'sample-btn';
            inBtn.dataset.sample = key;
            inBtn.textContent = `Sample Input ${nextIndex}`;
            inBtn.addEventListener('click', () => loadSample(key));

            const inCopyRow = document.createElement('div');
            inCopyRow.className = 'copy-row';
            const inCopyField = document.createElement('input');
            inCopyField.type = 'text';
            inCopyField.className = 'copy-field';
            inCopyField.id = 'copy-input-' + key;
            inCopyField.readOnly = true;
            inCopyField.value = samples[key] ? JSON.stringify(samples[key]) : '';
            const inCopyBtn = document.createElement('button');
            inCopyBtn.className = 'copy-btn';
            inCopyBtn.title = 'Copy Input';
            inCopyBtn.innerHTML = copyIconSvg;
            inCopyBtn.addEventListener('click', () => copySample(key, 'input'));
            inCopyRow.appendChild(inCopyField);
            inCopyRow.appendChild(inCopyBtn);

            leftItem.appendChild(inBtn);
            leftItem.appendChild(inCopyRow);

            // RIGHT: output item (button + copy field stacked)
            const rightItem = document.createElement('div');
            rightItem.className = 'sample-item';

            const initialIcon = statusIconFor('pending');
            outBtn = document.createElement('button');
            outBtn.className = 'sample-btn status-pending';
            outBtn.dataset.sample = outKey;
            outBtn.innerHTML = `${initialIcon} Sample Output ${nextIndex}`;
            outBtn.addEventListener('click', () => loadSample(outKey));

            const outCopyRow = document.createElement('div');
            outCopyRow.className = 'copy-row';
            const outCopyField = document.createElement('input');
            outCopyField.type = 'text';
            outCopyField.className = 'copy-field';
            outCopyField.id = 'copy-input-' + outKey;
            outCopyField.readOnly = true;
            outCopyField.value = samples[outKey] ? JSON.stringify(samples[outKey]) : '';
            const outCopyBtn = document.createElement('button');
            outCopyBtn.className = 'copy-btn';
            outCopyBtn.title = 'Copy Output';
            outCopyBtn.innerHTML = copyIconSvg;
            outCopyBtn.addEventListener('click', () => copySample(outKey, 'output'));
            outCopyRow.appendChild(outCopyField);
            outCopyRow.appendChild(outCopyBtn);

            rightItem.appendChild(outBtn);
            rightItem.appendChild(outCopyRow);

            row.appendChild(leftItem);
            row.appendChild(rightItem);
            section.appendChild(row);
        }
    } catch (e) {
        console.error('Failed to register new sample:', e);
    }

    // Send to backend (fire-and-log). Update status UI with result.
    if (window.postInputToServer) {
        try {
            const resp = await window.postInputToServer(parsed);
            console.log('Backend response for detect-clashes:', resp);
            // Replace the dummy output sample with the server response when available
            try {
                if (resp && outKey) {
                    const status = resp.status || (resp.result ? 'completed' : (resp.job_id ? 'processing' : 'failed'));
                    const icon = statusIconFor(status);
                    if (resp.result) {
                        samples[outKey] = resp.result;
                        // Update the copy field for the output sample if present
                        try {
                            const outField = document.getElementById('copy-input-' + outKey);
                            if (outField) outField.value = JSON.stringify(resp.result);
                        } catch (e) {
                            console.warn('Failed to update output copy field:', e);
                        }
                    }
                    if (outBtn) {
                        outBtn.classList.remove('status-pending','status-processing','status-completed','status-failed','ready');
                        outBtn.classList.add(`status-${status}`);
                        if (status === 'completed' && resp.result) outBtn.classList.add('ready');
                        outBtn.innerHTML = `${icon} Sample Output ${nextIndex}`;
                        outBtn.title = resp.job_id ? `Job ${resp.job_id} — ${status}` : `${status}`;
                    }
                }
            } catch (e) {
                console.error('Failed to apply server result to sample output:', e);
            }
            if (statusEl) { statusEl.textContent = ''; }
        } catch (err) {
            console.error('Failed to POST input to server:', err);
            if (statusEl) { statusEl.textContent = ''; }
        } finally {
            if (sendBtn) { sendBtn.disabled = false; sendBtn.textContent = 'Send'; }
        }
    } else {
        if (sendBtn) { sendBtn.disabled = false; sendBtn.textContent = 'Send'; }
        if (statusEl) { statusEl.textContent = ''; }
    }
}

// Toggle legend visibility based on sidebar checkbox
function updateLegendVisibility() {
    const cb = document.getElementById('show-legend-checkbox');
    const legend = document.getElementById('legend');
    if (!legend || !cb) return;
    const footerInner = document.querySelector('.footer-inner');
    if (cb.checked) {
        legend.style.display = 'flex';
        if (footerInner) footerInner.classList.add('legend-visible');
    } else {
        legend.style.display = 'none';
        if (footerInner) footerInner.classList.remove('legend-visible');
    }
}

// Attach checkbox listener
document.addEventListener('DOMContentLoaded', () => {
    const cb = document.getElementById('show-legend-checkbox');
    if (cb) {
        cb.addEventListener('change', updateLegendVisibility);
    }
    // ensure initial state
    updateLegendVisibility();
});

// POST GeoJSON to backend clash detection endpoint.
// Not wired to UI yet — call `postInputToServer(geojson)` when ready.
async function postInputToServer(geojson) {
    const url = '/api/v1/detect-clashes';
    try {
        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(geojson)
        });

        if (!resp.ok) {
            const text = await resp.text();
            throw new Error(`Server responded ${resp.status}: ${text}`);
        }

        const data = await resp.json();
        return data; // Caller handles the response
    } catch (err) {
        console.error('postInputToServer error:', err);
        throw err;
    }
}

// Expose samples object to the global window so inline scripts can access it
window.samples = samples;

// Populate any existing copy fields after DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        Object.keys(window.samples || {}).forEach(function(key) {
            const field = document.getElementById('copy-input-' + key);
            if (field && window.samples[key]) {
                field.value = JSON.stringify(window.samples[key]);
            }
        });
    } catch (e) {
        console.warn('Failed populating copy fields on load:', e);
    }
});

window.postInputToServer = postInputToServer;

// Initialize on load
init();

// Map JobStatus to an icon/emoji for button display
function statusIconFor(status) {
    switch ((status || '').toString().toLowerCase()) {
        case 'pending':
            return '⏳';
        case 'processing':
            return '🔄';
        case 'completed':
            return '✅';
        case 'failed':
            return '❌';
        default:
            return '❔';
    }
}
