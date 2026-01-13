import { useState, useEffect } from 'react';
import { Camera, Image as ImageIcon, Clock, CheckCircle2, Loader2, Wallet, Shield, TrendingUp, Calendar, Phone } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import { api, apiClient } from './services/api';
import { MonthPicker } from './components/MonthPicker';

// --- USER INTERFACE ---
interface User {
    id: number;
    username: string;
    display_name: string;
    role: string;
}

const LoginView = ({ onLogin }: { onLogin: (user: User) => void }) => {
    const [username, setUsername] = useState('admin');
    const [password, setPassword] = useState('admin123');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            // Call real API
            const response = await api.login(username, password);
            const { access_token } = response;

            // Save token
            localStorage.setItem('token', access_token);

            // Fetch user data
            const userData = await api.getCurrentUser();
            localStorage.setItem('user', JSON.stringify(userData));

            onLogin(userData);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Invalid credentials');
            setIsLoading(false);
        }
    };

    return (
        <div className="h-full flex flex-col justify-center px-8 relative">
            <div className="absolute top-0 left-0 right-0 h-1/2 bg-gradient-to-b from-neon-purple/20 to-transparent pointer-events-none" />

            <div className="text-center mb-12 relative z-10">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-3xl bg-finance-panel border border-white/10 mb-6 shadow-2xl shadow-neon-purple/20">
                    <Shield size={40} className="text-neon-purple" />
                </div>
                <h1 className="text-3xl font-bold text-white mb-2">Family Inc.</h1>
                <p className="text-neon-purple text-xs font-bold uppercase tracking-[0.2em]">Secure Mobile Terminal</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-6 relative z-10">
                <div className="space-y-2">
                    <label className="text-xs text-gray-500 font-medium ml-1">OPERATOR ID</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full bg-finance-panel border border-white/10 rounded-2xl py-4 px-5 text-white placeholder-gray-600 focus:outline-none focus:border-neon-purple/50 focus:bg-white/5 transition-all text-lg"
                        placeholder="username"
                        autoCapitalize="none"
                    />
                </div>

                <div className="space-y-2">
                    <label className="text-xs text-gray-500 font-medium ml-1">PASSWORD</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full bg-finance-panel border border-white/10 rounded-2xl py-4 px-5 text-white placeholder-gray-600 focus:outline-none focus:border-neon-purple/50 focus:bg-white/5 transition-all text-lg"
                        placeholder="••••••••"
                    />
                </div>

                <AnimatePresence>
                    {error && (
                        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="text-red-400 text-xs bg-red-500/10 p-3 rounded-xl border border-red-500/20 text-center">
                            {error}
                        </motion.div>
                    )}
                </AnimatePresence>

                <button
                    disabled={isLoading}
                    className="w-full bg-white text-black font-bold py-4 rounded-2xl hover:bg-gray-200 active:scale-95 transition-all flex items-center justify-center gap-2 mt-4"
                >
                    {isLoading ? <Loader2 className="animate-spin" /> : <span>Access Terminal</span>}
                </button>
            </form>

            <div className="absolute bottom-12 left-0 right-0 text-center">
                <p className="text-[10px] text-gray-600 font-mono">ENCRYPTED CONNECTION • V1.0.4</p>
            </div>
        </div>
    );
};

const MainApp = ({ currentUser, onLogout }: { currentUser: User, onLogout: () => void }) => {
    const [activeTab, setActiveTab] = useState<'scan' | 'wallet'>('scan');
    const [isScanning, setIsScanning] = useState(false);

    // Upload progress states
    const [uploadProgress, setUploadProgress] = useState(0);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'complete' | 'error'>('idle');
    const [uploadMessage, setUploadMessage] = useState('');

    // API Data States
    const [accounts, setAccounts] = useState<any[]>([]);
    const [transactions, setTransactions] = useState<any[]>([]);
    const [policies, setPolicies] = useState<any[]>([]);
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    // Pagination state
    const [currentPage, setCurrentPage] = useState(1);
    const [totalTransactions, setTotalTransactions] = useState(0);
    const itemsPerPage = 10;

    // Month filter state - default to current month
    const getCurrentMonth = () => {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    };
    const [selectedMonth, setSelectedMonth] = useState(getCurrentMonth());

    // Fetch data from API
    const fetchData = async () => {
        try {
            const skip = (currentPage - 1) * itemsPerPage;
            const [accountsData, txData, statsData, policiesData] = await Promise.all([
                api.getAccounts(),
                api.getTransactions(skip, itemsPerPage, selectedMonth),
                api.getDashboardStats(),
                api.getPolicies()
            ]);

            // Ensure all IDs are strings to prevent React key errors
            const safeAccounts = (accountsData || []).map((acc: any) => ({
                ...acc,
                id: String(acc.id)
            }));

            const safeTransactions = (txData || []).map((tx: any) => ({
                ...tx,
                id: String(tx.id)
            }));

            setAccounts(safeAccounts);
            setTransactions(safeTransactions);
            setStats(statsData);

            // Map backend policies to frontend format with safe IDs
            const mappedPolicies = (policiesData || []).map((p: any, i: number) => ({
                id: String(p.id),
                provider: String(p.provider || ''),
                type: String(p.type || '') + ' Policy',
                number: String(p.policy_number || ''),
                renewal: new Date(p.renewal_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                color: i % 2 === 0 ? 'bg-blue-600' : 'bg-yellow-500'
            }));
            setPolicies(mappedPolicies);
        } catch (error) {
            console.error('Failed to fetch mobile data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [currentPage, selectedMonth]); // Re-fetch when page or month changes

    // Get total transaction count
    useEffect(() => {
        const fetchTotal = async () => {
            try {
                const allTx = await api.getTransactions(0, 1000);
                setTotalTransactions(allTx.length);
            } catch (error) {
                console.error('Failed to get transaction count:', error);
            }
        };
        fetchTotal();

        // Auto-refresh every 30 seconds to sync with Admin changes
        const interval = setInterval(fetchData, 30000);

        return () => clearInterval(interval);
    }, []);

    // roomData removed - using dynamic account rendering instead

    // Mock data (keep for features not yet in API)
    // const policies = [...] // REPLACED BY STATE
    const nextDrop = { name: "Canada Child Benefit", date: "Nov 20", amount: 450.00 };

    const handleScan = () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.capture = 'environment';

        input.onchange = async (e: any) => {
            const file = e.target.files?.[0];
            if (!file) return;

            setIsScanning(true);
            setUploadStatus('uploading');
            setUploadProgress(0);
            setUploadMessage('Uploading receipt...');

            try {
                const formData = new FormData();
                formData.append('file', file);

                // Simulate upload progress
                const progressInterval = setInterval(() => {
                    setUploadProgress(prev => Math.min(prev + 10, 90));
                }, 200);

                await apiClient.post('/api/upload/receipt', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });

                clearInterval(progressInterval);
                setUploadProgress(100);
                setUploadStatus('processing');
                setUploadMessage('AI is analyzing your receipt...');

                // Wait for background processing
                await new Promise(resolve => setTimeout(resolve, 3000));

                setUploadStatus('complete');
                setUploadMessage('Receipt processed successfully!');

                // Refresh transactions
                const skip = (currentPage - 1) * itemsPerPage;
                const txData = await api.getTransactions(skip, itemsPerPage);
                const safeTransactions = (txData || []).map((tx: any) => ({
                    ...tx,
                    id: String(tx.id)
                }));
                setTransactions(safeTransactions);

                // Reset status after 2 seconds
                setTimeout(() => {
                    setUploadStatus('idle');
                    setUploadProgress(0);
                    setUploadMessage('');
                }, 2000);

            } catch (error: any) {
                setUploadStatus('error');
                setUploadMessage(error.response?.data?.detail || 'Upload failed');
                setTimeout(() => {
                    setUploadStatus('idle');
                    setUploadProgress(0);
                }, 3000);
            } finally {
                setIsScanning(false);
            }
        };
        input.click();
    };

    const handleUploadFile = () => {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'application/pdf,image/*';
        input.onchange = async (e: any) => {
            const file = e.target.files?.[0];
            if (!file) return;
            try {
                const formData = new FormData();
                formData.append('file', file);
                const response = await apiClient.post('/api/upload/receipt', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
                alert(`✅ Uploaded: ${response.data.filename}`);
            } catch (error: any) {
                alert(`❌ Failed: ${error.response?.data?.detail || error.message}`);
            }
        };
        input.click();
    };

    return (
        <div className="h-full flex flex-col relative">
            {/* Header */}
            <div className="px-6 mb-6 pt-2 flex-shrink-0">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h1 className="text-2xl font-bold text-white tracking-tight">Family Inc.</h1>
                        <p className="text-neon-purple text-xs font-medium uppercase tracking-wider">
                            {activeTab === 'scan' ? 'Transaction Terminal' : 'Digital Wallet'}
                        </p>
                    </div>
                    <div onClick={onLogout} className="w-10 h-10 rounded-full bg-finance-panel border border-grid-border overflow-hidden cursor-pointer active:scale-95 transition-transform" title="Tap to Logout">
                        <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${currentUser.username}`} alt="User" />
                    </div>
                </div>
            </div>

            {/* MAIN CONTENT AREA */}
            <div className="flex-1 overflow-y-auto px-6 space-y-6 pb-32 scrollbar-hide relative" style={{ WebkitOverflowScrolling: 'touch' }}>
                <AnimatePresence mode="wait">

                    {/* VIEW 1: SCANNER */}
                    {activeTab === 'scan' && (
                        <motion.div
                            key="scan"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 20 }}
                            className="space-y-6"
                        >
                            {/* Quick Stats */}
                            <div className="bg-gradient-to-r from-finance-panel to-black border border-grid-border p-4 rounded-2xl flex items-center justify-between">
                                <div>
                                    <div className="text-gray-400 text-xs mb-1">Monthly Spending</div>
                                    <div className="text-white font-mono font-medium">
                                        ${stats ? Math.abs(stats.cash_flow?.expenses || 0).toLocaleString() : '0'}
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-gray-400 text-xs mb-1">Net Worth</div>
                                    <div className="text-electric-green font-mono font-medium">
                                        ${stats ? stats.net_worth?.toLocaleString() : '0'}
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <h2 className="text-sm font-medium text-gray-300">New Entry</h2>
                                <div className="grid grid-cols-2 gap-4">
                                    <button onClick={handleScan} className={clsx("aspect-square bg-neon-purple/10 border border-neon-purple/20 rounded-2xl flex flex-col items-center justify-center gap-3 hover:bg-neon-purple/20 transition-all group relative overflow-hidden")}>
                                        <div className="absolute inset-0 bg-neon-purple/5 blur-xl group-hover:bg-neon-purple/10 transition-all" />
                                        <div className={clsx("w-14 h-14 rounded-full bg-neon-purple flex items-center justify-center text-white shadow-lg shadow-neon-purple/30", isScanning && "animate-pulse")}>
                                            <Camera size={24} />
                                        </div>
                                        <span className="text-neon-purple font-medium text-sm">Scan Receipt</span>
                                    </button>
                                    <button onClick={handleUploadFile} className="aspect-square bg-finance-panel border border-grid-border rounded-2xl flex flex-col items-center justify-center gap-3 hover:bg-white/5 transition-all text-gray-400 hover:text-white">
                                        <div className="w-14 h-14 rounded-full bg-gray-800 flex items-center justify-center"><ImageIcon size={24} /></div>
                                        <span className="font-medium text-sm">Upload File</span>
                                    </button>
                                </div>

                                {/* Upload Progress Indicator */}
                                {uploadStatus !== 'idle' && (
                                    <motion.div
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="mt-4 bg-finance-panel border border-grid-border p-4 rounded-xl"
                                    >
                                        <div className="flex items-center gap-3 mb-3">
                                            {uploadStatus === 'uploading' && <Loader2 className="animate-spin text-neon-purple" size={20} />}
                                            {uploadStatus === 'processing' && <Loader2 className="animate-spin text-electric-green" size={20} />}
                                            {uploadStatus === 'complete' && <CheckCircle2 className="text-electric-green" size={20} />}
                                            {uploadStatus === 'error' && <div className="text-red-400" style={{ fontSize: 20 }}>❌</div>}
                                            <span className={clsx(
                                                "text-sm font-medium",
                                                uploadStatus === 'error' ? 'text-red-400' : 'text-white'
                                            )}>
                                                {uploadMessage}
                                            </span>
                                        </div>

                                        {uploadStatus !== 'error' && (
                                            <div className="relative h-2 bg-gray-800 rounded-full overflow-hidden">
                                                <motion.div
                                                    className={clsx(
                                                        "absolute top-0 left-0 h-full rounded-full",
                                                        uploadStatus === 'complete' ? 'bg-electric-green' : 'bg-neon-purple'
                                                    )}
                                                    initial={{ width: '0%' }}
                                                    animate={{ width: `${uploadProgress}%` }}
                                                    transition={{ duration: 0.3 }}
                                                />
                                            </div>
                                        )}
                                    </motion.div>
                                )}
                            </div>

                            <div>
                                <div className="flex items-center justify-between mb-3">
                                    <h2 className="text-sm font-medium text-gray-300">Recent Snaps</h2>
                                    <MonthPicker
                                        selectedMonth={selectedMonth}
                                        onChange={(month) => {
                                            setSelectedMonth(month);
                                            setCurrentPage(1); // Reset to page 1 when month changes
                                        }}
                                        compact
                                    />
                                </div>
                                <div className="space-y-3">
                                    {loading ? (
                                        <div className="text-center py-8">
                                            <Loader2 className="animate-spin mx-auto text-neon-purple" size={32} />
                                            <p className="text-gray-500 text-sm mt-2">Loading transactions...</p>
                                        </div>
                                    ) : transactions.length === 0 ? (
                                        <div className="text-center py-8 text-gray-500 text-sm">
                                            No transactions yet
                                        </div>
                                    ) : (
                                        <>
                                            {transactions.map((tx: any) => (
                                                <div key={tx.id} className="bg-finance-panel border border-grid-border p-4 rounded-xl flex items-center justify-between">
                                                    <div className="flex items-center gap-3">
                                                        <div className="w-10 h-10 rounded-full flex items-center justify-center border bg-electric-green/10 border-electric-green/20 text-electric-green">
                                                            <CheckCircle2 size={18} />
                                                        </div>
                                                        <div>
                                                            <div className="text-white text-sm font-medium">{tx.merchant}</div>
                                                            <div className="text-gray-500 text-xs flex items-center gap-1"><Clock size={10} /> {tx.date}</div>
                                                        </div>
                                                    </div>
                                                    <div className="text-right">
                                                        <div className="text-white font-mono text-sm">${Math.abs(tx.amount).toFixed(2)}</div>
                                                        <div className="text-[10px] text-gray-500">{tx.category}</div>
                                                    </div>
                                                </div>
                                            ))}

                                            {/* Pagination */}
                                            {totalTransactions > itemsPerPage && (
                                                <div className="flex items-center justify-between pt-4 border-t border-grid-border">
                                                    <button
                                                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                                        disabled={currentPage === 1}
                                                        className="px-4 py-2 bg-finance-panel border border-grid-border rounded-lg text-sm text-gray-400 disabled:opacity-30 disabled:cursor-not-allowed"
                                                    >
                                                        Previous
                                                    </button>
                                                    <div className="text-sm text-gray-400">
                                                        Page {currentPage} of {Math.ceil(totalTransactions / itemsPerPage)}
                                                    </div>
                                                    <button
                                                        onClick={() => setCurrentPage(p => Math.min(Math.ceil(totalTransactions / itemsPerPage), p + 1))}
                                                        disabled={currentPage >= Math.ceil(totalTransactions / itemsPerPage)}
                                                        className="px-4 py-2 bg-finance-panel border border-grid-border rounded-lg text-sm text-gray-400 disabled:opacity-30 disabled:cursor-not-allowed"
                                                    >
                                                        Next
                                                    </button>
                                                </div>
                                            )}
                                        </>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    )}

                    {/* VIEW 2: WALLET */}
                    {activeTab === 'wallet' && (
                        <motion.div
                            key="wallet"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-8"
                        >
                            {/* Policy Cards (Apple Wallet Style Stack) */}
                            <div>
                                <h2 className="text-sm font-medium text-gray-300 mb-4 flex items-center gap-2">
                                    <Shield size={16} /> Digital Policies
                                </h2>
                                <div className="space-y-[-40px] hover:space-y-4 transition-all duration-300 pb-10">
                                    {policies.map((p) => (
                                        <div key={p.id} className={`${p.color} p-5 rounded-2xl shadow-2xl relative transform transition-transform hover:-translate-y-2 h-[160px] flex flex-col justify-between border-t border-white/20`}>
                                            <div className="flex justify-between items-start text-white">
                                                <div className="font-bold text-lg tracking-tight">{p.provider}</div>
                                                <Shield className="opacity-50" />
                                            </div>
                                            <div>
                                                <div className="text-white/60 text-xs uppercase tracking-wider mb-1">Policy Number</div>
                                                <div className="text-white font-mono text-xl tracking-widest shadow-black drop-shadow-sm">{p.number}</div>
                                            </div>
                                            <div className="flex justify-between items-end">
                                                <div className="text-xs text-white/80 bg-black/20 px-2 py-1 rounded">RN: {p.renewal}</div>
                                                <button className="bg-white text-black text-xs font-bold px-3 py-1.5 rounded-full flex items-center gap-1">
                                                    <Phone size={12} /> Support
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Registered Accounts - Dynamic */}
                            <div>
                                <h2 className="text-sm font-medium text-gray-300 mb-4 flex items-center gap-2">
                                    <TrendingUp size={16} /> Registered Accounts
                                </h2>
                                <div className="grid grid-cols-2 gap-4">
                                    {accounts.map((account) => (
                                        <div key={account.id} className="bg-finance-panel border border-grid-border p-4 rounded-2xl">
                                            <div className="text-gray-400 text-xs mb-1">{account.account_type}</div>
                                            <div className="text-gray-500 text-xs mb-2">{account.institution}</div>
                                            <div className="text-white font-mono text-sm font-bold">
                                                ${account.contribution_room?.toLocaleString() || '0'} Left
                                            </div>
                                            <div className="text-gray-400 text-xs mt-1">
                                                ${account.balance?.toLocaleString() || '0'} used
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Next Drop */}
                            <div>
                                <h2 className="text-sm font-medium text-gray-300 mb-4 flex items-center gap-2">
                                    <Calendar size={16} /> Incoming Benefits
                                </h2>
                                <div className="bg-gradient-to-r from-gray-900 to-black border border-grid-border p-4 rounded-xl flex items-center gap-4">
                                    <div className="bg-electric-green/10 text-electric-green p-3 rounded-full">
                                        <Wallet size={20} />
                                    </div>
                                    <div className="flex-1">
                                        <div className="text-white font-medium">{nextDrop.name}</div>
                                        <div className="text-xs text-gray-400">Government Deposit</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-white font-mono">+${nextDrop.amount}</div>
                                        <div className="text-xs text-electric-green">{nextDrop.date}</div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            {/* BOTTOM NAVIGATION (TAB SWITCHER) */}
            <div className="fixed bottom-6 left-0 right-0 px-6 flex justify-center pointer-events-none z-50">
                <div className="bg-black/90 backdrop-blur-xl border border-white/10 rounded-full py-2 px-6 flex items-center gap-12 pointer-events-auto shadow-2xl">
                    <button
                        onClick={() => setActiveTab('scan')}
                        className={clsx("flex flex-col items-center gap-1 transition-colors", activeTab === 'scan' ? "text-neon-purple" : "text-gray-500 hover:text-white")}
                    >
                        <Camera size={24} />
                        <span className="text-[10px] font-medium">Scan</span>
                    </button>

                    <div className="w-px h-8 bg-white/10"></div>

                    <button
                        onClick={() => setActiveTab('wallet')}
                        className={clsx("flex flex-col items-center gap-1 transition-colors", activeTab === 'wallet' ? "text-neon-purple" : "text-gray-500 hover:text-white")}
                    >
                        <Wallet size={24} />
                        <span className="text-[10px] font-medium">Wallet</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default function App() {
    const [currentUser, setCurrentUser] = useState<User | null>(null);

    return (
        <div className="h-full flex items-center justify-center bg-black p-4 md:p-8">
            <div className="w-full max-w-sm bg-finance-black border border-grid-border rounded-[2.5rem] overflow-y-auto shadow-2xl relative h-[800px] flex flex-col">

                {/* Status Bar */}
                <div className="px-6 py-4 flex justify-between items-center text-xs font-medium text-gray-400 absolute top-0 left-0 right-0 z-50">
                    <span>9:41</span>
                    <div className="flex gap-1.5">
                        <div className="w-4 h-4 bg-gray-800 rounded-sm flex items-center justify-center"><div className="w-2 h-2 bg-white rounded-full"></div></div>
                        <div className="w-4 h-4 bg-gray-800 rounded-sm"></div>
                    </div>
                </div>

                {/* CONTENT */}
                <div className="flex-1 pt-12">
                    {currentUser ? (
                        <MainApp currentUser={currentUser} onLogout={() => setCurrentUser(null)} />
                    ) : (
                        <LoginView onLogin={setCurrentUser} />
                    )}
                </div>

            </div>
        </div>
    );
};
