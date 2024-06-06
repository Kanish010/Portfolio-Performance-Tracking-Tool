document.addEventListener('DOMContentLoaded', function() {
    // Check localStorage for the user's theme preference
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
        document.getElementById('toggleMode').textContent = 'Toggle Light Mode';
    }

    document.getElementById('toggleMode').addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        this.textContent = isDarkMode ? 'Toggle Light Mode' : 'Toggle Dark Mode';
    });

    document.getElementById('optimizationForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(this);
        const stockDataInput = formData.get('stock_data');
        
        // Validate the stock data input
        if (!/^[a-zA-Z0-9,\s]+$/.test(stockDataInput)) {
            $('#errorModal .modal-body').text('Please separate stock tickers with commas.');
            $('#errorModal').modal('show');
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
                $('#errorModal .modal-body').text(data.error);
                $('#errorModal').modal('show');
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
                            </tr>                    `).join('')}
                </tbody>
            </table>
        `;
    })
    .catch(error => {
        console.error('Error:', error);
        $('#errorModal .modal-body').text('An error occurred while processing your request.');
        $('#errorModal').modal('show');
    });
});
});