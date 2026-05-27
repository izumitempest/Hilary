const rawBase = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const BASE_URL = rawBase.endsWith('/') ? rawBase.slice(0, -1) : rawBase;

async function handleResponse(response) {
  const contentType = response.headers.get('content-type');
  const isJson = contentType && contentType.includes('application/json');
  
  if (!response.ok) {
    let message = `Server Error (${response.status})`;
    if (isJson) {
      const errorData = await response.json();
      message = errorData.detail || message;
    } else {
      const text = await response.text();
      message = text || message;
    }
    throw new Error(message);
  }

  if (response.status === 204) return null;
  if (!isJson) {
      const text = await response.text();
      return text;
  }
  
  return response.json();
}

export const apiClient = {
  async request(path, options = {}) {
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    const url = `${BASE_URL}${cleanPath}`;
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const token = localStorage.getItem('token');
    if (token && !options.noAuth) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    return handleResponse(response);
  },

  async get(path) {
    return this.request(path, { method: 'GET' });
  },

  async post(path, data) {
    return this.request(path, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async postForm(path, formData) {
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    const url = `${BASE_URL}${cleanPath}`;
    const headers = {};
    const token = localStorage.getItem('token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });
    return handleResponse(response);
  },

  async register(username, email, password) {
    return this.post('/auth/register', { 
      full_name: username, 
      email, 
      password 
    });
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

    const data = await handleResponse(response);
    if (data && data.access_token) {
        localStorage.setItem('token', data.access_token);
        // Try to get full user profile
        try {
            const user = await this.get('/auth/me');
            return user;
        } catch (e) {
            return { email }; // Fallback
        }
    }
    return data;
  },

  async verifyEmail(token) {
    return this.get(`/auth/verify-email?token=${encodeURIComponent(token)}`);
  },

  async resendVerification(email) {
    return this.post('/auth/resend-verification', { email });
  },

  async delete(path) {
    return this.request(path, { method: 'DELETE' });
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};
