import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';
function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!username || !password) {
      setError('Por favor, completa todos los campos.');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
        credentials: 'include',
      });

      const data = await response.json();
      console.log('Login Response:', data);

      if (data.success) {
        onLoginSuccess(); // Actualiza el estado en App.jsx
        navigate('/'); // Redirige a Home
      } else {
        setError(data.message || 'Error en el inicio de sesión.');
      }
    } catch (err) {
      setError('Error de conexión con el servidor.');
      console.error(err);
    }
  };


  return (
    <div className="login-container">
      <div className="icon-wrapper">
        <svg
          width="32"
          height="32"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 15.1c.9-2.1.2-4.8-1.7-6.2-1.9-1.4-4.6-.9-6.2 1L8.9 8.2l-3.2-2.3-3.1 3 3.2 3.1 2.3-3.2 1.7 1.7c-1.9 1.7-2.4 4.3-1 6.2 1.4 1.9 4.1 2.6 6.2 1.7l4.4 2.8 2.3-3.7-2.8-4.4zM9.6 14.4l-1.7-1.7-2.3 3.2-3.1-3 3.2-3.1 2.3 3.2 1.7-1.7c1.6-1.9 4.3-2.4 6.2-1 1.9 1.4 2.6 4.1 1.7 6.2l-2.8 4.4-2.3-3.7 4.4-2.8c-2.1-.9-4.8-.2-6.2 1.7z" />
        </svg>
      </div>

      <h1 className="login-title">Sistema de Monitoreo Aéreo</h1>
      <p className="login-subtitle">AICM - Ciudad de México</p>

      <div className="login-box">
        <h2 className="form-title">Iniciar Sesión</h2>
        <p className="form-subtitle">Ingresa tus credenciales para acceder al sistema</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleLoginSubmit}>
          <div className="input-group">
            <label htmlFor="username">Usuario</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Ingresa tu usuario"
              className="input-field"
              required
            />
          </div>

          <div className="input-group">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Ingresa tu contraseña"
              className="input-field"
              required
            />
          </div>

          <button type="submit" className="login-button">
            Iniciar Sesión
          </button>
        </form>
      </div>
    </div>
  );
}

export default LoginPage;