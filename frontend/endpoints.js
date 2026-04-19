// Small module to hold API endpoint calls for the frontend
export async function postInputToServer(geojson) {
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
