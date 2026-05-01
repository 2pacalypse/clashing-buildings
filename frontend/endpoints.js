// Small module to hold API endpoint calls for the frontend
export async function postInputToServer(geojson) {
    const url = '/api/v1/detect-clashes';
    try {
        const body = typeof geojson === 'string' ? geojson : JSON.stringify(geojson);
        const resp = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body
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

export async function getResults(requestId) {
    const url = `/api/v1/results/${requestId}`;
    try {
        const resp = await fetch(url);

        if (!resp.ok) {
            const text = await resp.text();
            throw new Error(`Server responded ${resp.status}: ${text}`);
        }

        const data = await resp.json();
        return data;
    } catch (err) {
        console.error('getResults error:', err);
        throw err;
    }
}
