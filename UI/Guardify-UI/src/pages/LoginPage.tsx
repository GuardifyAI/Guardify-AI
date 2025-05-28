import { useState } from 'react';
import './LoginPage.css';
import { useNavigate } from 'react-router-dom';


export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const navigate = useNavigate();

const handleLogin = (e: React.FormEvent) => {
  e.preventDefault();
  if (email === 'guardifyai@gmail.com' && password === '1234') {
    navigate('/dashboard');
  } else {
    setError('Incorrect email or password.');
  }
};
  return (
    <div className="login-container">
      <form onSubmit={handleLogin} className="login-form">
        <h2>Login to Guardify</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}
