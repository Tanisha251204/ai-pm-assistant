const ENDPOINTS = {
    'prd': {
        url:   'http://127.0.0.1:8000/generate',
        field: 'prd',
        title: 'PRD'
    },
    'user-stories': {
        url:   'http://127.0.0.1:8000/user-stories',
        field: 'user_stories',
        title: 'User Stories'
    },
    'prioritize': {
        url:   'http://127.0.0.1:8000/prioritize',
        field: 'prioritization',
        title: 'MoSCoW Prioritization'
    }
};

let currentDocId = null;


async function generate(type, event) {

    if (event) event.preventDefault();

    const productName        = document.getElementById('productName').value;
    const productDescription = document.getElementById('productDescription').value;

    if (!productName.trim() || !productDescription.trim()) {
        alert('Please fill in both fields!');
        return;
    }

    const config = ENDPOINTS[type];
    const output = document.getElementById('outputContent');
    const title  = document.getElementById('outputTitle');

    // Highlight active button
    document.querySelectorAll('.tab-buttons button').forEach(b => {
        b.classList.remove('active');
    });
    document.getElementById('btn-' + type).classList.add('active');

    // Disable all buttons while generating
    document.querySelectorAll('.tab-buttons button').forEach(b => {
        b.disabled = true;
    });

    // Show loading state
    title.textContent  = config.title + ' — Generating...';
    output.textContent = 'Generating with Llama 3... please wait';

    try {
        const response = await fetch(config.url, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                product_name:        productName,
                product_description: productDescription
            })
        });

        const data = await response.json();

        title.textContent  = config.title;
        output.textContent = data[config.field];
        currentDocId       = data.doc_id;

        // Show download button
        const downloadBtn = document.getElementById('downloadBtn');
        if (downloadBtn) downloadBtn.style.display = 'block';

        console.log('Type:', type);
        console.log('Tokens used:', data.tokens_used);
        console.log('Doc ID:', data.doc_id);

    } catch (error) {
        output.textContent = 'Error: Could not connect to backend. Is your server running?';
        console.error(error);

    } finally {
        document.querySelectorAll('.tab-buttons button').forEach(b => {
            b.disabled = false;
        });
    }
}


async function loadHistory() {

    const historyDiv = document.getElementById('historyContent');
    historyDiv.textContent = 'Loading history...';

    try {
        const response = await fetch('http://127.0.0.1:8000/history');
        const data     = await response.json();

        if (data.total === 0) {
            historyDiv.textContent = 'No history yet. Generate something first!';
            return;
        }

        historyDiv.innerHTML = data.history.map(doc => `
            <div style="padding:10px; margin-bottom:8px;
                background:#0f172a; border-radius:8px;
                border-left:3px solid #6366f1;">
                <strong style="color:#e2e8f0;">${doc.product_name}</strong>
                <span style="color:#6366f1; margin-left:10px;
                    font-size:0.8rem;">${doc.doc_type}</span>
                <span style="color:#475569; float:right;
                    font-size:0.8rem;">${doc.tokens_used} tokens</span>
                <div style="color:#64748b; font-size:0.75rem; margin-top:4px;">
                    ${doc.created_at}
                </div>
            </div>
        `).join('');

    } catch (error) {
        historyDiv.textContent = 'Error loading history.';
    }
}


function downloadPDF() {

    if (!currentDocId) {
        alert('Please generate content first!');
        return;
    }

    window.open(
        `http://127.0.0.1:8000/download/${currentDocId}`,
        '_blank'
    );
}