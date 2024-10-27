import React, { useState } from 'react';
import axios from 'axios';

function Login({ setUser }) {
  const [isRegister, setIsRegister] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
  });
  const [message, setMessage] = useState('');

  const handleToggle = () => {
    setIsRegister(!isRegister);
    setMessage(''); // Clear message on toggle
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const url = isRegister ? 'http://127.0.0.1:5000/register' : 'http://127.0.0.1:5000/login';
    try {
      const response = await axios.post(url, formData);
      setMessage(response.data.message);

      if (response.data.success) {
        console.log(`User ID: ${response.data.user_id}`);
        setUser(response.data.user_id); // Pass user ID to App.js for state
      }
    } catch (error) {
      setMessage(error.response?.data?.message || 'An error occurred');
      console.error('Error details:', error.response?.data || error.message);
    }
  };

  return (
    <div
      className="h-screen flex items-center justify-center bg-cover bg-center relative"
      style={{
        backgroundImage: `url('/UBCO.jpg')`, // Adjust the path if necessary
      }}
    >
      <div className="absolute inset-0 bg-black opacity-50"></div>

      <div className="relative z-10 flex flex-col items-center w-full max-w-md px-8 py-10 bg-white bg-opacity-90 rounded-lg shadow-lg">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">
          {isRegister ? 'Register' : 'Login'}
        </h2>
        <form onSubmit={handleSubmit} className="w-full">
          {isRegister && (
            <div className="mb-4">
              <label className="block text-gray-800 text-sm font-semibold mb-2" htmlFor="email">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Enter your email"
                className="w-full p-2 border border-gray-300 rounded-md bg-white bg-opacity-90 text-gray-800 focus:outline-none focus:border-indigo-500"
              />
            </div>
          )}
          <div className="mb-4">
            <label className="block text-gray-800 text-sm font-semibold mb-2" htmlFor="username">
              Username
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Enter your username"
              className="w-full p-2 border border-gray-300 rounded-md bg-white bg-opacity-90 text-gray-800 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div className="mb-6">
            <label className="block text-gray-800 text-sm font-semibold mb-2" htmlFor="password">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              className="w-full p-2 border border-gray-300 rounded-md bg-white bg-opacity-90 text-gray-800 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <button
            type="submit"
            className="w-full py-2 px-4 bg-indigo-600 text-white font-bold rounded-md hover:bg-indigo-700 transition duration-200"
          >
            {isRegister ? 'Register' : 'Login'}
          </button>
        </form>
        {message && (
          <p className="mt-4 text-center text-sm text-red-600">
            {message}
          </p>
        )}
        <p className="mt-4 text-sm text-gray-600">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}
          <span
            onClick={handleToggle}
            className="text-indigo-600 hover:underline cursor-pointer ml-1"
          >
            {isRegister ? 'Login' : 'Register'}
          </span>
        </p>
      </div>
    </div>
  );
}

export default Login;