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


async function generate(type) {

    const productName        = document.getElementById('productName').value;
    const productDescription = document.getElementById('productDescription').value;

    if (!productName || !productDescription) {
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

        console.log('Type:', type);
        console.log('Tokens used:', data.tokens_used);

    } catch (error) {
        output.textContent = 'Error: Could not connect to backend. Is your server running?';
        console.error(error);
    }
}