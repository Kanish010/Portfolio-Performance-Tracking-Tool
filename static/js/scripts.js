document.getElementById('optimizationForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    const stockDataInput = formData.get('stock_data');
    
    // Validate the stock data input
    if (!/^[a-zA-Z0-9,\s]+$/.test(stockDataInput)) {
        alert('Please separate stock tickers with commas.');
        return;
    }
    
    const stockData = stockDataInput.split(',').map(stock => stock.trim().toUpperCase()).filter(stock => stock);

    const data = new URLSearchParams();
    data.append('optimization_method', formData.get('optimization_method'));
    stockData.forEach(stock => data.append('stock_data[]', stock));

    fetch('/optimize', {
        method: 'POST',
        body: data
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `
            <h2>Optimization Results</h2>
            <table class="table table-bordered table-striped">
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
        alert('An error occurred while processing your request.');
    });
});