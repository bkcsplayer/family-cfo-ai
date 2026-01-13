import axios from 'axios';

// API Base URL - use environment variable or relative path for nginx proxy
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Create axios instance
const apiClient = axios.create({
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
            // Unauthorized - clear token and redirect to login
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/';
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

    getRecentActivity: async () => {
        const response = await apiClient.get('/api/dashboard/recent-activity');
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

    approveTransaction: async (id: number) => {
        const response = await apiClient.put(`/api/transactions/${id}/approve`);
        return response.data;
    },

    updateTransaction: async (id: number, data: any) => {
        const response = await apiClient.put(`/api/transactions/${id}`, data);
        return response.data;
    },

    deleteTransaction: async (id: number) => {
        const response = await apiClient.delete(`/api/transactions/${id}`);
        return response.data;
    },

    rejectTransaction: async (id: number) => {
        const response = await apiClient.post(`/api/transactions/${id}/reject`);
        return response.data;
    },

    // Assets & Accounts
    getAssets: async () => {
        const response = await apiClient.get('/api/assets');
        return response.data;
    },

    addAsset: async (asset: any) => {
        const response = await apiClient.post('/api/assets', asset);
        return response.data;
    },

    updateAsset: async (id: number, data: any) => {
        const response = await apiClient.put(`/api/assets/${id}`, data);
        return response.data;
    },

    deleteAsset: async (id: number) => {
        await apiClient.delete(`/api/assets/${id}`);
    },

    getAccounts: async () => {
        const response = await apiClient.get('/api/accounts');
        return response.data;
    },

    getSubscriptions: async () => {
        const response = await apiClient.get('/api/subscriptions');
        return response.data;
    },

    getPolicies: async () => {
        const response = await apiClient.get('/api/insurance/');
        return response.data;
    },

    addAccount: async (account: any) => {
        const response = await apiClient.post('/api/accounts', account);
        return response.data;
    },

    updateAccount: async (id: number, data: any) => {
        const response = await apiClient.put(`/api/accounts/${id}`, data);
        return response.data;
    },

    deleteAccount: async (id: number) => {
        const response = await apiClient.delete(`/api/accounts/${id}`);
        return response.data;
    },

    updatePolicy: async (id: number, data: any) => {
        const response = await apiClient.put(`/api/insurance/${id}`, data);
        return response.data;
    },

    deletePolicy: async (id: number) => {
        const response = await apiClient.delete(`/api/insurance/${id}`);
        return response.data;
    },

    addPolicy: async (policy: any) => {
        const response = await apiClient.post('/api/insurance/', policy);
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

    categorizeBatch: async (transactionIds: number[]) => {
        const response = await apiClient.post('/api/ai/categorize-batch', {
            transaction_ids: transactionIds
        });
        return response.data;
    },

    getCategories: async () => {
        const response = await apiClient.get('/api/ai/categories');
        return response.data;
    },

    // Budget Management
    getBudgets: async (activeOnly = true) => {
        const response = await apiClient.get('/api/budgets/', {
            params: { active_only: activeOnly },
        });
        return response.data;
    },

    getBudgetStatus: async () => {
        const response = await apiClient.get('/api/budgets/status');
        return response.data;
    },

    createBudget: async (data: {
        category: string;
        monthly_limit: number;
        alert_threshold?: number;
    }) => {
        const response = await apiClient.post('/api/budgets/', data);
        return response.data;
    },

    updateBudget: async (id: number, data: any) => {
        const response = await apiClient.put(`/api/budgets/${id}`, data);
        return response.data;
    },

    deleteBudget: async (id: number) => {
        const response = await apiClient.delete(`/api/budgets/${id}`);
        return response.data;
    },

    checkBudgetAlerts: async () => {
        const response = await apiClient.get('/api/budgets/check-alerts');
        return response.data;
    },

    // Data Export
    exportTransactionsCSV: async (startDate?: string, endDate?: string, category?: string) => {
        const params: any = {};
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        if (category) params.category = category;

        const response = await apiClient.get('/api/export/transactions/csv', {
            params,
            responseType: 'blob',
        });

        // Trigger download
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `transactions_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    },

    exportTransactionsExcel: async (startDate?: string, endDate?: string) => {
        const params: any = {};
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;

        const response = await apiClient.get('/api/export/transactions/excel', {
            params,
            responseType: 'blob',
        });

        // Trigger download
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `transactions_${new Date().toISOString().split('T')[0]}.xlsx`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    },

    exportBudgetsExcel: async () => {
        const response = await apiClient.get('/api/export/budgets/excel', {
            responseType: 'blob',
        });

        // Trigger download
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `budgets_${new Date().toISOString().split('T')[0]}.xlsx`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    },

    exportMonthlyReport: async (year: number, month: number) => {
        const response = await apiClient.get('/api/export/monthly-report/csv', {
            params: { year, month },
            responseType: 'blob',
        });

        // Trigger download
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `monthly_report_${year}_${month}.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    },

    // Monitoring
    getSystemStatus: async () => {
        const response = await apiClient.get('/api/monitoring/system-status');
        return response.data;
    },

    // v3.0 API - Assets
    getAssetsV3: async () => {
        const response = await apiClient.get('/api/v3/assets');
        return response.data;
    },

    createAssetV3: async (data: any) => {
        const response = await apiClient.post('/api/v3/assets', data);
        return response.data;
    },

    updateAssetV3: async (id: number, data: any) => {
        const response = await apiClient.put(`/api/v3/assets/${id}`, data);
        return response.data;
    },

    deleteAssetV3: async (id: number) => {
        const response = await apiClient.delete(`/api/v3/assets/${id}`);
        return response.data;
    },

    // v3.0 API - Liabilities
    getLiabilities: async () => {
        const response = await apiClient.get('/api/v3/liabilities');
        return response.data;
    },

    createLiability: async (data: any) => {
        const response = await apiClient.post('/api/v3/liabilities', data);
        return response.data;
    },

    updateLiability: async (id: number, data: any) => {
        const response = await apiClient.put(`/api/v3/liabilities/${id}`, data);
        return response.data;
    },

    deleteLiability: async (id: number) => {
        const response = await apiClient.delete(`/api/v3/liabilities/${id}`);
        return response.data;
    },

    // v3.0 API - Net Worth
    getNetWorth: async () => {
        const response = await apiClient.get('/api/v3/net-worth');
        return response.data;
    },

    // v3.0 API - Categories
    getCategoriesV3: async (type?: string, isSystem?: boolean) => {
        const params: any = {};
        if (type) params.type = type;
        if (isSystem !== undefined) params.is_system = isSystem;
        const response = await apiClient.get('/api/categories/', { params });
        return response.data;
    },

    getCategoriesTree: async () => {
        const response = await apiClient.get('/api/categories/tree');
        return response.data;
    },

    createCategory: async (data: any) => {
        const response = await apiClient.post('/api/categories/', data);
        return response.data;
    },

    updateCategory: async (id: number, data: any) => {
        const response = await apiClient.put(`/api/categories/${id}`, data);
        return response.data;
    },

    deleteCategory: async (id: number) => {
        const response = await apiClient.delete(`/api/categories/${id}`);
        return response.data;
    },

    // Canadian Accounts (TFSA, RRSP, etc.)
    getCanadianAccounts: async () => {
        const response = await apiClient.get('/api/accounts');
        return response.data;
    },

    // v3.0 API - Government Benefits
    getGovBenefits: async (activeOnly: boolean = true) => {
        const response = await apiClient.get('/api/v3/gov-benefits/', {
            params: { active_only: activeOnly }
        });
        return response.data;
    },

    getGovBenefit: async (id: number) => {
        const response = await apiClient.get(`/api/v3/gov-benefits/${id}`);
        return response.data;
    },

    createGovBenefit: async (data: any) => {
        const response = await apiClient.post('/api/v3/gov-benefits/', data);
        return response.data;
    },

    updateGovBenefit: async (id: number, data: any) => {
        const response = await apiClient.put(`/api/v3/gov-benefits/${id}`, data);
        return response.data;
    },

    deleteGovBenefit: async (id: number) => {
        const response = await apiClient.delete(`/api/v3/gov-benefits/${id}`);
        return response.data;
    },

    getAnnualBenefitsSummary: async () => {
        const response = await apiClient.get('/api/v3/gov-benefits/summary/annual');
        return response.data;
    },

    // v3.0 API - Document Reviews (Scan & Approve Workflow)
    getPendingReviews: async (entityType?: string) => {
        const params: any = {};
        if (entityType) params.entity_type = entityType;
        const response = await apiClient.get('/api/v3/reviews/pending', { params });
        return response.data;
    },

    getPendingReview: async (id: number) => {
        const response = await apiClient.get(`/api/v3/reviews/${id}`);
        return response.data;
    },

    updatePendingReview: async (id: number, data: any) => {
        const response = await apiClient.put(`/api/v3/reviews/${id}`, data);
        return response.data;
    },

    approvePendingReview: async (id: number, finalData: any, notes?: string) => {
        const response = await apiClient.post(`/api/v3/reviews/${id}/approve`, {
            final_data: finalData,
            reviewer_notes: notes
        });
        return response.data;
    },

    rejectPendingReview: async (id: number, reason: string) => {
        const response = await apiClient.post(`/api/v3/reviews/${id}/reject`, {
            reviewer_notes: reason
        });
        return response.data;
    },

    uploadInsuranceDocument: async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await apiClient.post('/api/v3/reviews/upload/insurance', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    },
};

export default api;
