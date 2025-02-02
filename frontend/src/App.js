import React, { useState, useEffect } from 'react';
import apiEndpoints from './apiEndpoints';
import axios from 'axios';


function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState(false);

  const handleRegister = async (email, password, username) => {
    try {
        const response = await axios.post(`${apiEndpoints.url_auth}${apiEndpoints.auth.register}`, {
        email,
        password,
        username,
      });
        console.log(response.data);
        alert('Registration successful');
    } catch (err) {
        console.error(err.response?.data);
        setError(err.response?.data || 'Registration failed');
    }
  };

  const handleLogin = async (email, password, username) => {
    try {
      const response = await axios.post(`${apiEndpoints.url_auth}${apiEndpoints.auth.login}`, {
        email: email,
        password: password,
        username: username
      });
      console.log(response);
      console.log(response.data);
      console.log(response.data.token);
      setToken(response.data.access_token);
        console.log("User logged in:", response.data.access_token);
      setUser(response.data.user);
        console.log("User:", response.data.user);


    } catch (err) {
        console.error(err.response?.data);
        setError(err.response?.data || 'Login failed');
    }
  };

  const fetchProfile = async () => {
    try {
      const response = await axios.get(
        `${apiEndpoints.url_profile}${apiEndpoints.profile.getProfile.replace('<user>', user.username)}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setProfile(response.data);
    } catch (err) {
        console.error(err.response?.data);
        setError(err.response?.data || 'Failed to fetch profile');
    }
  };

  const saveProfile = async (newProfile) => {
    try {
      const response = await axios.post(
        `${apiEndpoints.url_profile}${apiEndpoints.profile.saveProfile}`,
        newProfile,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setProfile(response.data);
      alert('Profile saved');
    } catch (err) {
        console.error(err.response?.data);
        setError(err.response?.data || 'Failed to save profile');
    }
  };

  const searchRoom = async () => {
    try {
      const response = await axios.get(
        `${apiEndpoints.url_search_room}${apiEndpoints.search_room.findRoom}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert(`Room found: ${response.data.roomId}`);
    } catch (err) {
        console.error(err.response?.data);
        setError(err.response?.data || 'Failed to find room');
    }
  };

    useEffect(() => {
        if (token){
            setStatus(prevStatus => !prevStatus)
        }
    }, [token]);

  return (
    <div>
      <h1>React Frontend</h1>
      {status===false ? (
        <div>
          <h2>Register</h2>
          <RegisterForm onRegister={handleRegister} />
          <h2>Login</h2>
          <LoginForm onLogin={handleLogin} />
        </div>
      ) : (
        <div>
          <h2>Welcome, {user}</h2>
          <button onClick={fetchProfile}>View Profile</button>
          <button onClick={searchRoom}>Find a Room</button>
            <button onClick={saveProfile}>Save Profile</button>
          {profile && <ProfileForm profile={profile} onSave={saveProfile(profile)} />}
        </div>
      )}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

function RegisterForm({ onRegister }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');


  const handleSubmit = async (e) => {
    e.preventDefault();
      console.log(email, password, username); // Перевірте, чи всі значення коректно передаються
      await onRegister(email, password, username);
  };

  return (
      <form onSubmit={handleSubmit}>
          <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
          />
          <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
          />
          <input
              type="username"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
          />
          <button type="submit">Register</button>
      </form>
  );
}

function LoginForm({onLogin}) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [username, setUsername] = useState('');


    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log(email, password, username); // Перевірте, чи всі значення коректно передаються
       await onLogin(email, password, username);
  };

  return (
      <form onSubmit={handleSubmit}>
          <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
          />
          <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
          />
          <input
              type="username"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
          />
          <button type="submit">Login</button>
      </form>
  );
}

function ProfileForm({ profile, onSave }) {
    const [editedProfile, setEditedProfile] = useState(profile || {});
    const [countries, setCountries] = useState([]);

    useEffect(() => {
        // Завантаження списку країн
        const fetchCountries = async () => {
            try {
                const response = await fetch(`${apiEndpoints.url_profile}${apiEndpoints.profile.getCountries}`);
                if (response.ok) {
                    const data = await response.json();
                    setCountries(data);
                } else {
                    console.error('Не вдалося отримати список країн');
                }
            } catch (error) {
                console.error('Помилка під час отримання списку країн:', error);
            }
        };

        fetchCountries();
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setEditedProfile((prev) => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave(editedProfile);
    };

    return (
        <form onSubmit={handleSubmit}>
            <h3>Редагування профілю</h3>
            <div>
                <label htmlFor="first_name">Ім'я</label>
                <input
                    type="text"
                    id="first_name"
                    name="first_name"
                    value={editedProfile.first_name || ''}
                    onChange={handleChange}
                    placeholder="First Name"
                />
            </div>
            <div>
                <label htmlFor="last_name">Прізвище</label>
                <input
                    type="text"
                    id="last_name"
                    name="last_name"
                    value={editedProfile.last_name || ''}
                    onChange={handleChange}
                    placeholder="Last Name"
                />
            </div>
            <div>
                <label htmlFor="country">Країна</label>
                <select
                    id="country"
                    name="country"
                    value={editedProfile.country || ''}
                    onChange={handleChange}
                >
                    <option value="">Оберіть країну</option>
                    {countries.map((country) => (
                        <option key={country} value={country}>
                            {country}
                        </option>
                    ))}
                </select>
            </div>
            <div>
                <label htmlFor="age">Вік</label>
                <input
                    type="number"
                    id="age"
                    name="age"
                    value={editedProfile.age || ''}
                    onChange={handleChange}
                    placeholder="Age"
                />
            </div>
            <div>
                <label htmlFor="gender">Стать</label>
                <select
                    id="gender"
                    name="gender"
                    value={editedProfile.gender || ''}
                    onChange={handleChange}
                >
                    <option value="">Оберіть стать</option>
                    <option value="male">Чоловік</option>
                    <option value="female">Жінка</option>
                    <option value="other">Інша</option>
                </select>
            </div>
            <button type="submit">Зберегти профіль</button>
        </form>
    );
}

export default App;
