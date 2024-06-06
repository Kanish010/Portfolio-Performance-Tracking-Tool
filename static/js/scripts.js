document.getElementById('optimizationForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    const stockData = formData.get('stock_data').split(',').map(stock => stock.trim().toUpperCase()).filter(stock => stock);

    const data = new URLSearchParams();
    data.append('optimization_method', formData.get('optimization_method'));
    stockData.forEach(stock => data.append('stock_data[]', stock));

    fetch('/optimize', {
        method: 'POST',
        body: data
    })
    .then(response => response.json())
    .then(data => {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <h2>Optimization Results</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>Stock Ticker</th>
                        <th>Weight (%)</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.entries(data).map(([stock, weight]) => `
                        <tr>
                            <td>${stock.toUpperCase()}</td>
                            <td>${weight.toFixed(2)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});