import React, { createContext, useContext, useState, useEffect } from 'react';

// --- Types ---
export type TransactionStatus = 'draft' | 'Posted' | 'Pending';
export type TransactionType = 'expense' | 'income' | 'asset_purchase' | 'debt_payment';

export interface Transaction {
    id: string;
    merchant: string;
    date: string;
    amount: number;
    category: string;
    status: TransactionStatus;
    type: TransactionType;
    // Amortization Logic
    isAmortized?: boolean;
    amortizationMonths?: number;
    // Mortgage Logic
    isMortgage?: boolean;
    principalAmount?: number; // Goes to Equity
    interestAmount?: number;  // Goes to OpEx
    escrowAmount?: number;    // Goes to OpEx (Tax)
    // Asset Link
    assetId?: string;
}

export interface Asset {
    id: string;
    name: string;
    type: 'RealEstate' | 'Vehicle' | 'Stock';
    value: number;
    equity?: number; // For real estate
}

export interface Subscription {
    id: string;
    name: string;
    cost: number;
    billingCycle: 'Monthly' | 'Yearly' | 'Quarterly';
    paymentMethod: string;
    merchantKeyword: string;
    lastPaidDate?: string;
    status: 'Active' | 'Paused';
}

export interface InsurancePolicy {
    id: string;
    provider: string; // e.g., State Farm
    type: 'Auto' | 'Home' | 'Life' | 'Health' | 'Disability';
    policyNumber: string;
    renewalDate: string;
    premium: number; // cost
    frequency: 'Monthly' | 'Yearly';
    insuredItem?: string; // e.g., "Tesla Model Y"
}

export interface RegisteredAccount {
    id: string;
    type: 'TFSA' | 'RRSP' | 'RESP' | 'FHSA';
    institution: string; // e.g., Questrade
    holder: string; // e.g., "Dad", "Mom"
    currentValue: number;
    contributionRoom: number; // Remaining room
}

export interface User {
    id: string;
    username: string;
    displayName: string;
    role: 'Admin' | 'Editor' | 'Viewer';
    status: 'Active' | 'Inactive';
    lastLogin?: string;
}

export interface StoreContextType {
    transactions: Transaction[];
    assets: Asset[];
    subscriptions: Subscription[];
    insurancePolicies: InsurancePolicy[];
    registeredAccounts: RegisteredAccount[];
    users: User[];
    currentUser: User | null;
    kpis: {
        netWorth: number;
        cashFlowIncome: number;
        cashFlowExpense: number;
        burnRate: number;
    };
    actions: {
        addTransaction: (transaction: Omit<Transaction, 'id' | 'status'>) => void;
        addAsset: (asset: Omit<Asset, 'id'>) => void;
        approveTransaction: (id: string, updates: Partial<Transaction>) => void;
        deleteTransaction: (id: string) => void;
        updateSubscription: (id: string, updates: Partial<Subscription>) => void;
        // New Actions
        addInsurancePolicy: (policy: Omit<InsurancePolicy, 'id'>) => void;
        addRegisteredAccount: (account: Omit<RegisteredAccount, 'id'>) => void;
        // Auth Actions
        login: (username: string) => boolean;
        logout: () => void;
        addUser: (user: Omit<User, 'id' | 'lastLogin'>) => void;
    };
}

const StoreContext = createContext<StoreContextType | null>(null);

// --- Mock Data ---
const INITIAL_USERS: User[] = [
    { id: 'u1', username: 'admin', displayName: 'CFO (You)', role: 'Admin', status: 'Active', lastLogin: 'Just now' },
    { id: 'u2', username: 'partner', displayName: 'Partner', role: 'Editor', status: 'Active', lastLogin: '2 hours ago' },
    { id: 'u3', username: 'kid1', displayName: 'Intern', role: 'Viewer', status: 'Active', lastLogin: '1 day ago' },
];

const INITIAL_ASSETS: Asset[] = [
    { id: 'a1', name: 'Main Residence', type: 'RealEstate', value: 1450000, equity: 942000 },
    { id: 'a2', name: '2023 Toyota Tundra', type: 'Vehicle', value: 65200, equity: 65200 },
    { id: 'a3', name: 'Apple Stock Portfolio', type: 'Stock', value: 120400, equity: 120400 },
    { id: 'a4', name: 'Nvidia Stock', type: 'Stock', value: 1000, equity: 1000 },
];

const INITIAL_SUBSCRIPTIONS: Subscription[] = [
    { id: 's1', name: 'Netflix Premium', cost: 22.99, billingCycle: 'Monthly', paymentMethod: 'Amex 1234', merchantKeyword: 'netflix', status: 'Active', lastPaidDate: '2025-10-15' },
    { id: 's2', name: 'Rogers Internet', cost: 85.00, billingCycle: 'Monthly', paymentMethod: 'Checking 001', merchantKeyword: 'rogers', status: 'Active', lastPaidDate: '2025-10-20' },
    { id: 's3', name: 'Amazon Prime', cost: 119.00, billingCycle: 'Yearly', paymentMethod: 'Amex 1234', merchantKeyword: 'prime', status: 'Active', lastPaidDate: '2025-01-05' },
];

const INITIAL_INSURANCE: InsurancePolicy[] = [
    { id: 'i1', provider: 'State Farm', type: 'Auto', policyNumber: 'SF-998822', renewalDate: '2025-11-01', premium: 185.00, frequency: 'Monthly', insuredItem: '2023 Toyota Tundra' },
    { id: 'i2', provider: 'Sun Life', type: 'Life', policyNumber: 'SL-112233', renewalDate: '2026-01-15', premium: 1200.00, frequency: 'Yearly', insuredItem: 'Dad Life Insurance' },
];

const INITIAL_ACCOUNTS: RegisteredAccount[] = [
    { id: 'r1', type: 'TFSA', institution: 'Questrade', holder: 'Dad', currentValue: 85000, contributionRoom: 10000 },
    { id: 'r2', type: 'RRSP', institution: 'Wealthsimple', holder: 'Mom', currentValue: 142000, contributionRoom: 35000 },
    { id: 'r3', type: 'RESP', institution: 'RBC', holder: 'Kid 1', currentValue: 24000, contributionRoom: 2500 },
];

const INITIAL_TRANSACTIONS: Transaction[] = [
    // Drafts (Incoming for Review)
    // Card A: Perfect Match
    { id: 't_netflix', merchant: 'NETFLIX.COM *subscription', date: '2025-11-16', amount: 22.99, category: 'Entertainment', status: 'draft', type: 'expense' },
    // Card B: Price Mismatch
    { id: 't_rogers', merchant: 'ROGERS *INTERNET BILL', date: '2025-11-21', amount: 120.50, category: 'Utilities', status: 'draft', type: 'expense' },
    // Card C: New Subscription
    { id: 't_adobe', merchant: 'Adobe Creative Cloud', date: '2025-11-18', amount: 54.99, category: 'Software', status: 'draft', type: 'expense' },
    // Others
    { id: 't1', merchant: 'City Treasurer', date: '2025-10-25', amount: 4800.00, category: 'Taxes - Property', status: 'draft', type: 'expense' },

    // Posted History (for Charts)
    { id: 'h1', merchant: 'Salary', date: '2025-10-15', amount: 6000.00, category: 'Income', status: 'Posted', type: 'income' },
    { id: 'h2', merchant: 'Salary', date: '2025-10-30', amount: 6000.00, category: 'Income', status: 'Posted', type: 'income' },
    { id: 'h3', merchant: 'Utilities', date: '2025-10-01', amount: 250.00, category: 'Utilities', status: 'Posted', type: 'expense' },
];

export const StoreProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [currentUser, setCurrentUser] = useState<User | null>(null);
    const [users, setUsers] = useState<User[]>(INITIAL_USERS);
    const [transactions, setTransactions] = useState<Transaction[]>(INITIAL_TRANSACTIONS);
    const [assets, setAssets] = useState<Asset[]>(INITIAL_ASSETS);
    const [subscriptions, setSubscriptions] = useState<Subscription[]>(INITIAL_SUBSCRIPTIONS);
    const [insurancePolicies, setInsurancePolicies] = useState<InsurancePolicy[]>(INITIAL_INSURANCE);
    const [registeredAccounts, setRegisteredAccounts] = useState<RegisteredAccount[]>(INITIAL_ACCOUNTS);
    const [kpis, setKpis] = useState({ netWorth: 0, cashFlowIncome: 0, cashFlowExpense: 0, burnRate: 0 });

    // Recalculate KPIs whenever data changes
    useEffect(() => {
        let income = 0;
        let expense = 0;
        let amortizedDailyBurn = 0;

        // 1. Calculate Cash Flow (This Month)
        transactions.filter(t => t.status === 'Posted').forEach(t => {
            if (t.type === 'income') {
                income += t.amount;
            } else if (t.type === 'expense') {
                // If amortized, we still paid cash NOW, so cash flow hit is full amount.
                // But for "Burn Rate" (OpEx), we treat it differently.
                expense += t.amount;

                if (t.isAmortized && t.amortizationMonths) {
                    amortizedDailyBurn += (t.amount / t.amortizationMonths);
                } else {
                    amortizedDailyBurn += t.amount;
                }
            } else if (t.type === 'debt_payment') {
                // Mortgage: Cash out is total amount
                expense += t.amount;
                // Burn Rate: Only Interest + Escrow is burn. Principal is savings.
                if (t.interestAmount) amortizedDailyBurn += t.interestAmount;
                if (t.escrowAmount) amortizedDailyBurn += t.escrowAmount;
            }
        });

        // 2. Net Worth = Sum(Assets) + Cash(Simulated as Income - Expense) + Registered Accounts
        const assetValue = assets.reduce((acc, curr) => acc + (curr.equity || curr.value), 0);
        const regAccountValue = registeredAccounts.reduce((acc, curr) => acc + curr.currentValue, 0); // Add Registered Accounts to Net Worth
        const cashOnHand = income - expense; // Simple simulation starting from 0
        const totalNetWorth = assetValue + regAccountValue + cashOnHand + 120000; // Base baseline

        setKpis({
            netWorth: totalNetWorth,
            cashFlowIncome: income,
            cashFlowExpense: expense,
            burnRate: amortizedDailyBurn // Simply treating all posted expenses as "this month" bucket for demo
        });

    }, [transactions, assets, registeredAccounts]);

    const actions = {
        addTransaction: (data: Omit<Transaction, 'id' | 'status'>) => {
            const newTx: Transaction = {
                id: Date.now().toString(),
                status: 'draft',
                ...data
            };
            setTransactions(prev => [newTx, ...prev]);
        },
        addAsset: (asset: Omit<Asset, 'id'>) => {
            const newAsset: Asset = {
                id: Date.now().toString(),
                ...asset
            };
            setAssets(prev => [...prev, newAsset]);
        },
        approveTransaction: (id: string, updates: Partial<Transaction>) => {
            setTransactions(prev => prev.map(t => t.id === id ? { ...t, ...updates, status: 'Posted' } : t));

            // Special Logic: If Mortgage Principal Link, update Asset Equity
            if (updates.isMortgage && updates.principalAmount && updates.assetId) {
                setAssets(prev => prev.map(a => a.id === updates.assetId ? { ...a, equity: (a.equity || 0) + (updates.principalAmount || 0) } : a));
            }
        },
        deleteTransaction: (id: string) => {
            setTransactions(prev => prev.filter(t => t.id !== id));
        },
        updateSubscription: (id: string, updates: Partial<Subscription>) => {
            setSubscriptions(prev => prev.map(s => s.id === id ? { ...s, ...updates } : s));
        },
        addInsurancePolicy: (policy: Omit<InsurancePolicy, 'id'>) => {
            setInsurancePolicies(prev => [...prev, { id: Date.now().toString(), ...policy }]);
        },
        addRegisteredAccount: (account: Omit<RegisteredAccount, 'id'>) => {
            setRegisteredAccounts(prev => [...prev, { id: Date.now().toString(), ...account }]);
        },
        login: (username: string) => {
            const user = users.find(u => u.username === username);
            if (user) {
                setCurrentUser(user);
                return true;
            }
            return false;
        },
        logout: () => {
            setCurrentUser(null);
        },
        addUser: (user: Omit<User, 'id' | 'lastLogin'>) => {
            setUsers(prev => [...prev, { id: Date.now().toString(), lastLogin: 'Never', ...user }]);
        }
    };

    return (
        <StoreContext.Provider value={{ transactions, assets, subscriptions, insurancePolicies, registeredAccounts, users, currentUser, kpis, actions }}>
            {children}
        </StoreContext.Provider>
    );
};

export const useStore = () => {
    const context = useContext(StoreContext);
    if (!context) throw new Error("useStore must be used within StoreProvider");
    return context;
};
