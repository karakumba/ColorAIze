import React, { useState } from 'react';
import axios from 'axios';

// const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_BASE = 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);


  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
    setResult(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API_BASE}/api/colorize`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>🎨 ColorAIze</h1>
        <p>Colorize your black and white photos with AI</p>
      </header>

      <main>
        <form onSubmit={handleSubmit}>
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            disabled={loading}
          />
          <button type="submit" disabled={!file || loading}>
            {loading ? 'Processing...' : 'Colorize Image'}
          </button>
        </form>

        {error && <div className="error">{error}</div>}

        {result && (
          <div className="result">
            <h3>Result</h3>
            <img
              src={`${API_BASE}${result.preview_url}`}
              alt="Colorized"
            />
            <a
              href={`${API_BASE}${result.download_url}`}
              download
            >
              Download Result
            </a>
          </div>
        )}

        {loading && (
          <div className="loading">
            <p>Processing image... This may take up to 60 seconds.</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;