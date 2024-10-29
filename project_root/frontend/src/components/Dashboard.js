import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Dashboard({ userId, onViewPortfolio }) {
  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchPortfolios = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:5000/portfolio/${userId}`);
        setPortfolios(response.data.portfolios || []);
        setLoading(false);
      } catch (err) {
        setError(err.response?.data?.message || 'Error loading portfolios');
        setLoading(false);
      }
    };

    fetchPortfolios();
  }, [userId]);

  const handleCreatePortfolio = () => {
    // Navigate to a portfolio creation page or open a modal
  };

  const handleViewPortfolio = (portfolioName) => {
    if (onViewPortfolio) onViewPortfolio(portfolioName); // Call the onViewPortfolio prop if defined
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-600">{error}</div>;

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">Dashboard</h1>

      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-700">Your Portfolios</h2>
        <button
          onClick={handleCreatePortfolio}
          className="px-4 py-2 bg-indigo-600 text-white font-bold rounded-md hover:bg-indigo-700 transition"
        >
          + Create New Portfolio
        </button>
      </div>

      {portfolios.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {portfolios.map((portfolio) => (
            <div
              key={portfolio.portfolio_id}
              className="bg-white p-4 rounded-lg shadow-lg flex flex-col justify-between"
            >
              <h3 className="text-xl font-bold text-gray-800 mb-2">{portfolio.name}</h3>
              <p className="text-gray-600 mb-4">{portfolio.description || 'No description available'}</p>
              <button
                className="mt-auto px-4 py-2 bg-indigo-600 text-white font-semibold rounded-md hover:bg-indigo-700 transition"
                onClick={() => handleViewPortfolio(portfolio.name)}
              >
                View Details
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-700 text-center">You have no portfolios yet. Start by creating one!</p>
      )}
    </div>
  );
}

export default Dashboard;