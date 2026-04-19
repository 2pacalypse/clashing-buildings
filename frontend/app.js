import { sampleInputOne, sampleInputTwo, samples } from './data.js';
import { postInputToServer } from './endpoints.js';
import { init as initScene, loadSample, clearScene, renderGeoJSON, renderAllSelectedSamples, resetCamera, topDownView, sideView, clearSelection } from './scene.js';

// Copy icon (emoji)
const copyIconSvg = '📋';

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

// Expose samples object to the global window so inline scripts can access it
window.samples = samples;

// Add ready inputs aliases for quick-loading/copying (placeholder -> sampleInputOne)
samples.ready_XXS = sampleInputOne;
samples.ready_XS = sampleInputOne;
samples.ready_S = sampleInputOne;
samples.ready_M = sampleInputOne;
samples.ready_L = sampleInputOne;
samples.ready_XL = sampleInputOne;

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
