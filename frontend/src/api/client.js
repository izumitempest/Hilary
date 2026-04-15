const rawBase = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const BASE_URL = rawBase.endsWith('/') ? rawBase.slice(0, -1) : rawBase;

export const apiClient = {
  async post(path, data, authenticated = true) {
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    const headers = {
      'Content-Type': 'application/json',
    };

    if (authenticated) {
      const token = localStorage.getItem('token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    const response = await fetch(`${BASE_URL}${cleanPath}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }

    return response.json();
  },

  async get(path, authenticated = true) {
    const headers = {};

    if (authenticated) {
      const token = localStorage.getItem('token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    const response = await fetch(`${BASE_URL}${cleanPath}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      throw new Error('Request failed');
    }

    return response.json();
  },

  async clearHistory() {
    const token = localStorage.getItem('token');
    const response = await fetch(`${BASE_URL}/chat/history`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) throw new Error('Failed to clear history');
    return response.json();
  },

  async register(username, email, password) {
    const response = await fetch(`${BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, full_name: username }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  },

  async login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    if (!response.ok) {
      const text = await response.text();
      let detail = 'Invalid credentials';
      try {
        const err = JSON.parse(text);
        detail = err.detail || detail;
      } catch (e) { /* fallback to default */ }
      throw new Error(detail);
    }

    const data = await response.json();
    localStorage.setItem('token', data.access_token);
    
    // FETCH THE USER DATA IMMEDIATELY
    const userResponse = await fetch(`${BASE_URL}/auth/me`, {
      headers: { 'Authorization': `Bearer ${data.access_token}` }
    });
    
    if (userResponse.ok) {
        const userData = await userResponse.json();
        return userData;
    }
    
    return { email }; // Fallback
  },

  logout() {
    localStorage.removeItem('token');
  }
};
