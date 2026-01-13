import axios from 'axios';

// API Base URL - use environment variable or default to v2.0
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:6501';

// Create axios instance
export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add JWT token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Unauthorized - clear token and reload
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.reload();
        }
        return Promise.reject(error);
    }
);

// API Functions
export const api = {
    // Authentication
    login: async (username: string, password: string) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await axios.post(`${API_BASE_URL}/api/auth/token`, formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        return response.data;
    },

    getCurrentUser: async () => {
        const response = await apiClient.get('/api/auth/me');
        return response.data;
    },

    // Dashboard
    getDashboardStats: async () => {
        const response = await apiClient.get('/api/dashboard/stats');
        return response.data;
    },

    // Transactions
    getTransactions: async (skip = 0, limit = 100, month?: string) => {
        const params: any = { skip, limit };
        if (month) {
            params.month = month;
        }
        const response = await apiClient.get('/api/transactions/', {
            params,
        });
        return response.data;
    },

    createTransaction: async (transaction: any) => {
        const response = await apiClient.post('/api/transactions/', transaction);
        return response.data;
    },

    // Assets & Accounts
    getAccounts: async () => {
        const response = await apiClient.get('/api/accounts/');
        return response.data;
    },

    getSubscriptions: async () => {
        const response = await apiClient.get('/api/subscriptions/');
        return response.data;
    },

    getPolicies: async () => {
        const response = await apiClient.get('/api/insurance/');
        return response.data;
    },

    // AI Categorization
    categorizeTransaction: async (merchant: string, amount: number) => {
        const response = await apiClient.post('/api/ai/categorize-transaction', {
            merchant,
            amount
        });
        return response.data;
    },
};

export default api;
