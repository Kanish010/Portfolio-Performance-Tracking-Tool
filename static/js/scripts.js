document.getElementById('optimizationForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    const stockData = formData.get('stock_data').split('\n').map(stock => stock.trim()).filter(stock => stock);

    const data = new URLSearchParams();
    data.append('num_stocks', formData.get('num_stocks'));
    data.append('optimization_method', formData.get('optimization_method'));
    stockData.forEach(stock => data.append('stock_data[]', stock));

    fetch('/optimize', {
        method: 'POST',
        body: data
    })
    .then(response => response.json())
    .then(data => {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '<h2>Optimization Results</h2>';
        for (const [stock, weight] of Object.entries(data)) {
            resultsDiv.innerHTML += `<p>${stock}: ${weight.toFixed(2)}%</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});