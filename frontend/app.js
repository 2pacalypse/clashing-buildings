// Rotate the coordinates inside each ring of Polygon or MultiPolygon features
function rotateCoordinates(sampleKey) {
    if (!window.samples || !window.samples[sampleKey]) return;
    // Deep clone the sample to avoid mutating all references
    const orig = window.samples[sampleKey];
    const updated = JSON.parse(JSON.stringify(orig));
    function rotateRing(ring) {
        if (!Array.isArray(ring) || ring.length < 4) return ring;
        // Remove last point (should be same as first)
        const closed = JSON.stringify(ring[0]) === JSON.stringify(ring[ring.length - 1]);
        const core = closed ? ring.slice(0, -1) : ring.slice();
        // Rotate by a random offset
        const offset = Math.floor(Math.random() * core.length);
        const rotated = core.slice(offset).concat(core.slice(0, offset));
        // Re-close the ring
        return closed ? rotated.concat([rotated[0]]) : rotated;
    }
    if (updated.features && Array.isArray(updated.features)) {
        updated.features.forEach(f => {
            if (!f.geometry || !f.geometry.type || !f.geometry.coordinates) return;
            if (f.geometry.type === 'Polygon') {
                if (Array.isArray(f.geometry.coordinates)) {
                    f.geometry.coordinates = f.geometry.coordinates.map(ring => rotateRing(ring));
                }
            } else if (f.geometry.type === 'MultiPolygon') {
                if (Array.isArray(f.geometry.coordinates)) {
                    f.geometry.coordinates = f.geometry.coordinates.map(poly =>
                        Array.isArray(poly) ? poly.map(ring => rotateRing(ring)) : poly
                    );
                }
            }
        });
    }
    window.samples[sampleKey] = updated;
    // Update the text field
    const field = document.getElementById('copy-input-' + sampleKey);
    if (field) {
        field.value = JSON.stringify(updated);
        // Flash orange checkmark
        const original = field.value;
        const originalAlign = field.style.textAlign || '';
        const originalColor = field.style.color || '';
        try {
            field.style.textAlign = 'center';
            field.style.color = '#ff8800';
            field.classList.add('flash');
            field.value = '🔄 Coordinates rotated';
        } catch (e) {}
        setTimeout(() => {
            try {
                field.classList.remove('flash');
                field.style.textAlign = originalAlign;
                field.style.color = originalColor;
                field.value = JSON.stringify(updated);
            } catch (e) {}
        }, 1200);
    }
}
window.rotateCoordinates = rotateCoordinates;
// Shuffle the order of buildings in a ready sample and update the text field with flash
window.shuffleBuildings = function(sampleKey) {
    if (!window.samples || !window.samples[sampleKey]) return;
    // Deep clone the sample to avoid mutating all references
    const orig = window.samples[sampleKey];
    const updated = JSON.parse(JSON.stringify(orig));
    if (updated.features && Array.isArray(updated.features)) {
        // Fisher-Yates shuffle
        for (let i = updated.features.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [updated.features[i], updated.features[j]] = [updated.features[j], updated.features[i]];
        }
    }
    window.samples[sampleKey] = updated;
    // Update the text field
    const field = document.getElementById('copy-input-' + sampleKey);
    if (field) {
        field.value = JSON.stringify(updated);
        // Flash blue checkmark
        const original = field.value;
        const originalAlign = field.style.textAlign || '';
        const originalColor = field.style.color || '';
        try {
            field.style.textAlign = 'center';
            field.style.color = '#1a4f8f';
            field.classList.add('flash');
            field.value = '🔀 Shuffled';
        } catch (e) {}
        setTimeout(() => {
            try {
                field.classList.remove('flash');
                field.style.textAlign = originalAlign;
                field.style.color = originalColor;
                field.value = JSON.stringify(updated);
            } catch (e) {}
        }, 1200);
    }
};
// Increment all heights in a ready sample and update the text field with flash
window.incrementHeights = function(sampleKey) {
    if (!window.samples || !window.samples[sampleKey]) return;
    // Deep clone the sample to avoid mutating all references
    const orig = window.samples[sampleKey];
    const updated = JSON.parse(JSON.stringify(orig));
    if (updated.features && Array.isArray(updated.features)) {
        updated.features.forEach(f => {
            if (f.properties && typeof f.properties.height === 'number') {
                f.properties.height += 1;
            }
        });
    }
    window.samples[sampleKey] = updated;
    // Update the text field
    const field = document.getElementById('copy-input-' + sampleKey);
    if (field) {
        field.value = JSON.stringify(updated);
        // Flash green checkmark
        const original = field.value;
        const originalAlign = field.style.textAlign || '';
        const originalColor = field.style.color || '';
        try {
            field.style.textAlign = 'center';
            field.style.color = '#1a8f2b';
            field.classList.add('flash');
            field.value = '✅ Updated';
        } catch (e) {}
        setTimeout(() => {
            try {
                field.classList.remove('flash');
                field.style.textAlign = originalAlign;
                field.style.color = originalColor;
                field.value = JSON.stringify(updated);
            } catch (e) {}
        }, 1200);
    }
};
import { sampleInputOne, sampleInputTwo, samples, test100Buildings, test200Buildings, test300Buildings, test400Buildings, test500Buildings, test600Buildings } from './data.js';
import { postInputToServer, getResults } from './endpoints.js';
import { init as initScene, loadSample, clearScene, renderGeoJSON, renderAllSelectedSamples, resetCamera, topDownView, sideView, clearSelection } from './scene.js';

// Copy icon (emoji)
const copyIconSvg = '📋';

// Track active polling intervals to cancel them if needed
const activePolls = new Map();

// Expose scene controls imported from `scene.js`
window.loadSample = loadSample;
window.clearInput = function() {
    document.querySelectorAll('.sample-btn').forEach(btn => btn.classList.remove('active'));
    clearSelection();
    const legend = document.getElementById('legend');
    if (legend) legend.innerHTML = '';
};
window.resetCamera = resetCamera;
window.topDownView = topDownView;
window.sideView = sideView;

// Poll for job results with animated hourglass feedback
async function pollForResults(jobId, outBtn, outKey, outCopyField, requestStartTime) {
    let pollCount = 0;
    const maxPolls = 600; // Max 5 minutes of polling (600 * 500ms)
    const outputIndex = outKey.match(/\d+/)?.[0] || '';

    const pollInterval = setInterval(async () => {
        pollCount++;

        // Stop polling if max attempts reached
        if (pollCount > maxPolls) {
            clearInterval(pollInterval);
            if (outBtn && outBtn.dataset.displayInterval) {
                clearInterval(parseInt(outBtn.dataset.displayInterval));
            }
            activePolls.delete(jobId);
            if (outBtn) {
                outBtn.disabled = false;
                outBtn.classList.remove('polling');
                outBtn.textContent = `⏱️ Sample Output ${outputIndex} (timeout)`;
            }
            return;
        }

        try {
            const result = await getResults(jobId);
            const status = result.status || (result.result ? 'completed' : 'pending');

            if (status === 'completed' && result.result) {
                // Job completed - stop polling and update UI
                clearInterval(pollInterval);
                if (outBtn && outBtn.dataset.displayInterval) {
                    clearInterval(parseInt(outBtn.dataset.displayInterval));
                }
                activePolls.delete(jobId);

                samples[outKey] = result.result;
                if (outCopyField) outCopyField.value = JSON.stringify(result.result);

                if (outBtn) {
                    const elapsedMs = Date.now() - requestStartTime;
                    const elapsedSeconds = (elapsedMs / 1000).toFixed(2);

                    outBtn.disabled = false;
                    outBtn.classList.remove('polling');
                    outBtn.classList.remove('status-pending', 'status-processing');
                    outBtn.classList.add('status-completed', 'ready');
                    outBtn.innerHTML = `✅ Sample Output ${outputIndex} (${elapsedSeconds}s)`;
                    outBtn.title = `Job ${jobId} — completed in ${elapsedSeconds}s`;
                    outBtn.style.opacity = '';
                    outBtn.style.backgroundColor = '';
                    outBtn.style.color = '';
                    delete outBtn.dataset.displayInterval;
                }
            } else if (status === 'failed') {
                // Job failed - stop polling and show error
                clearInterval(pollInterval);
                if (outBtn && outBtn.dataset.displayInterval) {
                    clearInterval(parseInt(outBtn.dataset.displayInterval));
                }
                activePolls.delete(jobId);

                if (outBtn) {
                    outBtn.disabled = false;
                    outBtn.classList.remove('polling');
                    outBtn.classList.remove('status-pending', 'status-processing');
                    outBtn.classList.add('status-failed');
                    outBtn.innerHTML = `❌ Sample Output ${outputIndex}`;
                    outBtn.title = `Job ${jobId} — failed`;
                    outBtn.style.opacity = '';
                    outBtn.style.backgroundColor = '';
                    outBtn.style.color = '';
                    delete outBtn.dataset.displayInterval;
                }
            }
        } catch (err) {
            console.error('Error polling for results:', err);
            // Continue polling on error
        }
    }, 500);

    activePolls.set(jobId, pollInterval);
}

// Expose scene controls imported from `scene.js`
window.loadSample = loadSample;
window.clearInput = function() {
    document.querySelectorAll('.sample-btn').forEach(btn => btn.classList.remove('active'));
    clearSelection();
    const legend = document.getElementById('legend');
    if (legend) legend.innerHTML = '';
};
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

    // Capture request start time BEFORE making the POST request
    const requestStartTime = Date.now();

    // Show the timer immediately when Send is clicked
    if (outBtn) {
        outBtn.disabled = true;
        outBtn.classList.add('polling');
        outBtn.innerHTML = `⏳ Sample Output ${nextIndex} (0.00s)`;
        
        // Start display timer to show elapsed time
        const displayInterval = setInterval(() => {
            if (!outBtn || !outBtn.classList.contains('polling')) {
                clearInterval(displayInterval);
                return;
            }
            const elapsedMs = Date.now() - requestStartTime;
            const elapsedSeconds = (elapsedMs / 1000).toFixed(2);
            outBtn.innerHTML = `⏳ Sample Output ${nextIndex} (${elapsedSeconds}s)`;
        }, 100);
        
        // Store the display interval so it can be cleared later
        outBtn.dataset.displayInterval = displayInterval;
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
                        
                        // Calculate elapsed time from POST request start to now
                        const elapsedMs = Date.now() - requestStartTime;
                        const elapsedSeconds = (elapsedMs / 1000).toFixed(2);
                        
                        // Handle different status outcomes
                        if (status === 'pending' || status === 'processing') {
                            // Already showing timer from before POST, just update status for styling
                            // Timer will continue running via the displayInterval set earlier
                        } else if (status === 'completed' && resp.result) {
                            // Immediate result - stop the timer and show final time with checkmark
                            if (outBtn.dataset.displayInterval) {
                                clearInterval(parseInt(outBtn.dataset.displayInterval));
                                delete outBtn.dataset.displayInterval;
                            }
                            outBtn.classList.remove('polling');
                            outBtn.disabled = false;
                            outBtn.innerHTML = `✅ Sample Output ${nextIndex} (${elapsedSeconds}s)`;
                        } else {
                            // Failed or other status - stop timer
                            if (outBtn.dataset.displayInterval) {
                                clearInterval(parseInt(outBtn.dataset.displayInterval));
                                delete outBtn.dataset.displayInterval;
                            }
                            outBtn.classList.remove('polling');
                            outBtn.disabled = false;
                            outBtn.innerHTML = `${icon} Sample Output ${nextIndex}`;
                        }
                        outBtn.title = resp.job_id ? `Job ${resp.job_id} — ${status}` : `${status}`;
                    }

                    // Start polling if job is pending or processing
                    if ((status === 'pending' || status === 'processing') && resp.job_id) {
                        if (outBtn) {
                            outBtn.disabled = true;
                            outBtn.classList.add('polling');
                        }
                        const outCopyField = document.getElementById('copy-input-' + outKey);
                        pollForResults(resp.job_id, outBtn, outKey, outCopyField, requestStartTime);
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

// Expose samples object to the global window so inline scripts can access it
window.samples = samples;

// Add ready inputs aliases for quick-loading/copying (placeholder -> sampleInputOne)
samples.ready_XXS = test100Buildings;
samples.ready_XS = test200Buildings;
samples.ready_S = test300Buildings;
samples.ready_M = test400Buildings;
samples.ready_L = test500Buildings;
samples.ready_XL = test600Buildings;

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
initScene();

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
