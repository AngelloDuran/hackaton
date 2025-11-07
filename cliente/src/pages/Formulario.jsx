import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// (Opcional: puedes instalar 'react-icons' y descomentar esto)
// import { FaUser, FaLock } from 'react-icons/fa'; 

/**
 * Componente de Login adaptado para el Sistema de Monitoreo Aéreo.
 * Recibe 'onLoginSuccess' desde App.jsx para actualizar el estado de autenticación.
 */
function LoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(''); // Estado para mensajes de error
  const navigate = useNavigate();

  const handleLoginSubmit = async (e) => {
    e.preventDefault(S);
    setError(''); // Limpiar errores previos

    if (!username || !password) {
      setError('Por favor, completa todos los campos.');
      return;
    }

    try {
      // 1. Llamar al endpoint /api/login del backend (el correcto)
      const response = await fetch('http://localhost:5000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
        credentials: 'include', // ¡CRÍTICO! Para enviar y recibir la cookie de sesión
      });

      const data = await response.json();

      console.log('Login Response:', data);

      if (data && data.success) {
        // 2. Si es exitoso, avisar a App.jsx
        onLoginSuccess();
        // 3. Navegar a la página principal ("index" o dashboard)
        navigate('/');
      } else {
        setError(data?.message || 'Error en el inicio de sesión.');
      }
    } catch (err) {
      setError('Error de conexión con el servidor.');
      console.error('Fetch Error:', err);
    }
  };

  return (
    // Contenedor principal que imita el diseño de tu imagen
    <div style={styles.container}>
      {/* Icono de avión */}
      <div style={styles.iconWrapper}>
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15.1c.9-2.1.2-4.8-1.7-6.2-1.9-1.4-4.6-.9-6.2 1L8.9 8.2l-3.2-2.3-3.1 3 3.2 3.1 2.3-3.2 1.7 1.7c-1.9 1.7-2.4 4.3-1 6.2 1.4 1.9 4.1 2.6 6.2 1.7l4.4 2.8 2.3-3.7-2.8-4.4zM9.6 14.4l-1.7-1.7-2.3 3.2-3.1-3 3.2-3.1 2.3 3.2 1.7-1.7c1.6-1.9 4.3-2.4 6.2-1 1.9 1.4 2.6 4.1 1.7 6.2l-2.8 4.4-2.3-3.7 4.4-2.8c-2.1-.9-4.8-.2-6.2 1.7z"/>
        </svg>
      </div>

      {/* Títulos */}
      <h1 style={styles.title}>Sistema de Monitoreo Aéreo</h1>
      <p style={styles.subtitle}>AICM - Ciudad de México</p>
      
      {/* Caja del Formulario */}
      <div style={styles.loginBox}>
        <h2 style={styles.formTitle}>Iniciar Sesión</h2>
        <p style={styles.formSubtitle}>Ingresa tus credenciales para acceder al sistema</p>
        
        {/* Mensaje de Error */}
        {error && (
          <div style={styles.error}>
            {error}
          </div>
        )}

        <form onSubmit={handleLoginSubmit}>
          <div style={styles.inputGroup}>
            <label htmlFor="username">Usuario</label>
            {/* (Opcional: puedes agregar el ícono aquí) */}
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Ingresa tu usuario"
              style={styles.input}
              required
            />
          </div>
          
          <div style={styles.inputGroup}>
            <label htmlFor="password">Contraseña</label>
            {/* (Opcional: puedes agregar el ícono aquí) */}
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Ingresa tu contraseña"
              style={styles.input}
              required
            />
          </div>
          
          <button type="submit" style={styles.button}>
            Iniciar Sesión
          </button>
        </form>
      </div>
    </div>
  );
}

// --- Estilos de ejemplo para replicar tu diseño ---
// (Puedes reemplazar esto con tus archivos CSS)
const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    background: '#0a4da2', // Azul principal
    fontFamily: 'Arial, sans-serif',
    padding: '20px',
    boxSizing: 'border-box'
  },
  iconWrapper: {
    width: '64px',
    height: '64px',
    borderRadius: '50%',
    background: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#0a4da2',
    margin: '0 auto 20px auto',
    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
  },
  title: {
    color: 'white',
    textAlign: 'center',
    fontWeight: 'bold',
    fontSize: '2.5rem'
  },
  subtitle: {
    color: 'white',
    textAlign: 'center',
    fontSize: '1.2rem',
    marginBottom: '30px',
    opacity: 0.9
  },
  loginBox: {
    background: 'white',
    borderRadius: '16px',
    padding: '40px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
    width: '100%',
    maxWidth: '450px'
  },
  formTitle: {
    fontSize: '1.8rem',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '8px',
    textAlign: 'center'
  },
  formSubtitle: {
    color: '#666',
    marginBottom: '25px',
    textAlign: 'center'
  },
  inputGroup: {
    marginBottom: '20px'
  },
  input: {
    width: '100%',
    padding: '14px 16px',
    border: '1px solid #ddd',
    borderRadius: '8px',
    boxSizing: 'border-box',
    marginTop: '5px',
    fontSize: '1rem',
    background: '#f9f9f9'
  },
  button: {
    width: '100%',
    padding: '14px',
    background: '#0041a3', // Azul oscuro del botón
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: 'bold',
    transition: 'background 0.3s'
  },
  error: {
    color: 'red',
    background: '#ffebee',
    border: '1px solid red',
    padding: '10px',
    borderRadius: '8px',
    textAlign: 'center',
    marginBottom: '15px'
  }
};

export default LoginPage;