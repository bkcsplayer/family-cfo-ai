import { useState, useEffect } from 'react';
import { BentoBox } from '../components/ui/BentoBox';
import { TrendingUp, AlertCircle, FileText, CheckCircle2, Plus, X, Loader2, Download, ChevronDown } from 'lucide-react';
import { BarChart, Bar, ResponsiveContainer } from 'recharts';
import { type TransactionType } from '../context/StoreContext';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../services/api';
import { useViewNavigation } from '../context/ViewNavigationContext';
import { SystemMonitor } from '../components/SystemMonitor';
import { MonthPicker } from '../components/MonthPicker';

export const Dashboard = () => {
    const { navigateTo } = useViewNavigation();
    const [transactions, setTransactions] = useState<any[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [showExportMenu, setShowExportMenu] = useState(false);
    const [dashboardStats, setDashboardStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [netWorthData, setNetWorthData] = useState<any>(null);
    const [assetsV3, setAssetsV3] = useState<any[]>([]);

    // Month filter state - default to current month
    const getCurrentMonth = () => {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    };
    const [selectedMonth, setSelectedMonth] = useState(getCurrentMonth());

    // Fetch dashboard stats and transactions from API
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [stats, txData, netWorth, assets] = await Promise.all([
                    api.getDashboardStats(),
                    api.getTransactions(0, 100, selectedMonth),
                    api.getNetWorth().catch(() => null),
                    api.getAssetsV3().catch(() => [])
                ]);
                setDashboardStats(stats);
                setNetWorthData(netWorth);
                setAssetsV3(assets || []);
                // Convert all transaction IDs to strings
                const safeTxData = (txData || []).map((tx: any) => ({
                    ...tx,
                    id: String(tx.id)
                }));
                setTransactions(safeTxData);
            } catch (error) {
                console.error('Failed to fetch dashboard data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [selectedMonth]); // Re-fetch when month changes

    // Calculate specific view data
    const inboxItems = transactions.filter(t => t.status === 'draft' || t.status === 'Pending');
    const inboxCount = inboxItems.length;

    // Use v3.0 API data if available, fallback to v2.0, then mock data
    const netWorth = netWorthData?.net_worth || dashboardStats?.net_worth || 0;
    const cashFlowIncome = dashboardStats?.cash_flow?.income || 12000;
    const cashFlowExpense = dashboardStats?.cash_flow?.expenses || 8200;
    const burnRate = dashboardStats?.burn_rate || 8200;

    const monthlyCashflow = [
        { name: 'Prev', income: 10500, expense: 7800 },
        { name: 'Last', income: 11200, expense: 8000 },
        { name: 'Curr', income: cashFlowIncome, expense: cashFlowExpense },
    ];

    // Manual Entry State
    const [newTx, setNewTx] = useState({
        merchant: '',
        amount: '',
        category: '',
        type: 'expense' as TransactionType,
        date: new Date().toISOString().split('T')[0]
    });

    const handleAdd = async () => {
        if (!newTx.merchant || !newTx.amount) return;

        try {
            await api.createTransaction({
                merchant: newTx.merchant,
                amount: parseFloat(newTx.amount),
                category: newTx.category || 'Uncategorized',
                date: newTx.date,
                status: 'draft' // Add as draft for review
            });

            setIsModalOpen(false);
            setNewTx({ merchant: '', amount: '', category: '', type: 'expense', date: new Date().toISOString().split('T')[0] });

            // Show success message and navigate to review workbench
            alert('Transaction added to review queue!');
            navigateTo('transactions');
        } catch (error) {
            console.error('Failed to create transaction:', error);
            alert('Failed to create transaction. Please try again.');
        }
    };

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <Loader2 className="animate-spin text-neon-purple" size={48} />
            </div>
        );
    }

    return (
        <div className="p-6 h-full overflow-y-auto overflow-x-hidden relative">
            <header className="mb-6 flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-light text-white mb-1 tracking-tight">CFO <span className="text-gray-500">Cockpit</span></h1>
                    <p className="text-gray-500 text-sm">Family Enterprise Overview • {new Date().toLocaleDateString()}</p>
                </div>
                <div className="flex gap-3 items-center">
                    {/* Month Picker */}
                    <MonthPicker
                        selectedMonth={selectedMonth}
                        onChange={setSelectedMonth}
                        compact
                    />

                    {/* Export Dropdown */}
                    <div className="relative">
                        <button
                            onClick={() => setShowExportMenu(!showExportMenu)}
                            className="bg-finance-panel border border-grid-border hover:border-electric-green/50 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-all"
                        >
                            <Download size={18} />
                            <span>Export</span>
                            <ChevronDown size={16} />
                        </button>
                        <AnimatePresence>
                            {showExportMenu && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="absolute right-0 mt-2 w-56 bg-finance-panel border border-grid-border rounded-lg shadow-xl z-50"
                                >
                                    <div className="p-2">
                                        <button
                                            onClick={() => { api.exportTransactionsCSV(); setShowExportMenu(false); }}
                                            className="w-full text-left px-4 py-2 rounded-lg hover:bg-finance-black text-white transition-colors"
                                        >
                                            Export Transactions CSV
                                        </button>
                                        <button
                                            onClick={() => { api.exportTransactionsExcel(); setShowExportMenu(false); }}
                                            className="w-full text-left px-4 py-2 rounded-lg hover:bg-finance-black text-white transition-colors"
                                        >
                                            Export Transactions Excel
                                        </button>
                                        <button
                                            onClick={() => { api.exportBudgetsExcel(); setShowExportMenu(false); }}
                                            className="w-full text-left px-4 py-2 rounded-lg hover:bg-finance-black text-white transition-colors"
                                        >
                                            Export Budgets
                                        </button>
                                        <button
                                            onClick={() => {
                                                const now = new Date();
                                                api.exportMonthlyReport(now.getFullYear(), now.getMonth() + 1);
                                                setShowExportMenu(false);
                                            }}
                                            className="w-full text-left px-4 py-2 rounded-lg hover:bg-finance-black text-white transition-colors"
                                        >
                                            Export Monthly Report
                                        </button>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="bg-neon-purple hover:bg-neon-purple/80 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors shadow-lg shadow-neon-purple/20"
                    >
                        <Plus size={18} />
                        <span>Manual Entry</span>
                    </button>
                </div>
            </header>

            {/* Manual Entry Modal */}
            <AnimatePresence>
                {isModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setIsModalOpen(false)} />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-finance-panel border border-grid-border rounded-2xl p-6 w-full max-w-md relative z-10 shadow-2xl"
                        >
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-xl font-bold text-white">New Transaction</h3>
                                <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-white"><X size={20} /></button>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <label className="text-xs text-gray-400 block mb-1">Merchant / Source</label>
                                    <input
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none"
                                        value={newTx.merchant}
                                        onChange={e => setNewTx({ ...newTx, merchant: e.target.value })}
                                        placeholder="e.g. Starbucks"
                                        autoFocus
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-xs text-gray-400 block mb-1">Amount</label>
                                        <input
                                            type="number"
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none font-mono"
                                            value={newTx.amount}
                                            onChange={e => setNewTx({ ...newTx, amount: e.target.value })}
                                            placeholder="0.00"
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs text-gray-400 block mb-1">Type</label>
                                        <select
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none"
                                            value={newTx.type}
                                            onChange={e => setNewTx({ ...newTx, type: e.target.value as TransactionType })}
                                        >
                                            <option value="expense">Expense</option>
                                            <option value="income">Income</option>
                                            <option value="debt_payment">Debt Payment</option>
                                        </select>
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-xs text-gray-400 block mb-1">Category</label>
                                        <input
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none"
                                            value={newTx.category}
                                            onChange={e => setNewTx({ ...newTx, category: e.target.value })}
                                            placeholder="e.g. Dining"
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs text-gray-400 block mb-1">Date</label>
                                        <input
                                            type="date"
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none"
                                            value={newTx.date}
                                            onChange={e => setNewTx({ ...newTx, date: e.target.value })}
                                        />
                                    </div>
                                </div>

                                <button
                                    onClick={handleAdd}
                                    className="w-full bg-neon-purple hover:bg-neon-purple/80 text-white font-bold py-3 rounded-xl mt-4 transition-colors"
                                >
                                    Add to Queue
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* Top Row: KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                {/* Net Worth - v3.0 Real Data */}
                <BentoBox title="Total Net Worth" action={
                    netWorthData && (
                        <span className="text-xs text-electric-green">v3.0 API</span>
                    )
                }>
                    <div className="flex flex-col h-full justify-between">
                        <div>
                            <div className="text-4xl font-mono font-medium text-white tracking-tighter mb-2">
                                ${netWorth.toLocaleString()}
                            </div>
                            {netWorthData ? (
                                <div className="space-y-1">
                                    <div className="flex justify-between text-xs">
                                        <span className="text-gray-400">Assets:</span>
                                        <span className="text-electric-green font-mono">
                                            ${parseFloat(netWorthData.total_assets || 0).toLocaleString()}
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-xs">
                                        <span className="text-gray-400">Liabilities:</span>
                                        <span className="text-muted-red font-mono">
                                            -${parseFloat(netWorthData.total_liabilities || 0).toLocaleString()}
                                        </span>
                                    </div>
                                    <div className="pt-2 border-t border-grid-border flex items-center gap-2 text-electric-green text-sm">
                                        <TrendingUp size={14} />
                                        <span className="text-xs">Live from v3.0 Database</span>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex items-center gap-2 text-gray-500 text-sm bg-gray-500/10 w-fit px-2 py-1 rounded">
                                    <AlertCircle size={14} />
                                    <span className="text-xs">No v3.0 data yet</span>
                                </div>
                            )}
                        </div>
                    </div>
                </BentoBox>

                {/* Monthly Cash Flow */}
                <BentoBox title="Monthly Cash Flow (Accrual)">
                    <div className="flex items-end gap-2 mb-4">
                        <div className="flex-1">
                            <span className="text-xs text-gray-400 block mb-1">Revenue</span>
                            <span className="text-xl font-mono text-electric-green">+${cashFlowIncome.toLocaleString()}</span>
                        </div>
                        <div className="flex-1">
                            <span className="text-xs text-gray-400 block mb-1">Expenses</span>
                            <span className="text-xl font-mono text-muted-red">-${cashFlowExpense.toLocaleString()}</span>
                        </div>
                    </div>
                    <div className="bg-white/5 px-3 py-2 rounded text-sm font-medium mb-2 text-center border border-grid-border">
                        Net: <span className={cashFlowIncome - cashFlowExpense > 0 ? "text-electric-green" : "text-signal-orange"}>
                            {(cashFlowIncome - cashFlowExpense) > 0 ? '+' : ''}${(cashFlowIncome - cashFlowExpense).toLocaleString()}
                        </span>
                    </div>
                    <div className="h-16">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={monthlyCashflow}>
                                <Bar dataKey="income" fill="#28cd41" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="expense" fill="#ff453a" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </BentoBox>

                {/* Burn Rate */}
                <BentoBox title="MoM OpEx Burn Rate">
                    <div className="flex flex-col h-full justify-center">
                        <div className="text-center">
                            <div className="text-3xl font-mono text-white mb-2 py-2 border-b border-grid-border inline-block">
                                ${burnRate.toLocaleString(undefined, { maximumFractionDigits: 0 })}<span className="text-lg text-gray-500">/mo</span>
                            </div>
                            <p className="text-xs text-gray-400 max-w-[200px] mx-auto mt-2">
                                Reflects amortized impact of major purchases + interest.
                            </p>
                        </div>
                    </div>
                </BentoBox>
            </div>

            {/* Middle Row: Action & Assets */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                {/* Inbox */}
                <BentoBox className="lg:col-span-2"
                    title="Review Queue (Inbox)"
                    action={inboxCount > 0 ? <span className="bg-signal-orange text-black font-bold px-2 py-0.5 rounded text-xs animate-pulse">{inboxCount} PENDING</span> : <span className="text-gray-600 text-xs">ALL CLEAR</span>}
                >
                    {inboxCount === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-2 opacity-50">
                            <CheckCircle2 size={48} />
                            <p>No pending transactions.</p>
                        </div>
                    ) : (
                        <div className="flex flex-col h-full">
                            <div className="flex-1 flex flex-col gap-2 overflow-y-auto max-h-[400px] pr-2">
                                {inboxItems.slice(0, 10).map((item) => (
                                    <div key={item.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors group cursor-pointer border border-transparent hover:border-grid-border">
                                        <div className="flex items-center gap-4">
                                            <div className="w-10 h-10 rounded-full bg-finance-black flex items-center justify-center border border-grid-border text-gray-400">
                                                {item.category === 'Mortgage' || item.amount > 1000 ? <AlertCircle size={18} className="text-signal-orange" /> : <FileText size={18} />}
                                            </div>
                                            <div>
                                                <div className="text-white font-medium">{item.merchant}</div>
                                                <div className="text-xs text-gray-400">{item.date} • {item.category}</div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-6">
                                            <div className="text-right">
                                                <div className="font-mono text-white">${item.amount.toLocaleString()}</div>
                                            </div>
                                            <button
                                                onClick={() => navigateTo('transactions')}
                                                className="bg-neon-purple/20 text-neon-purple hover:bg-neon-purple hover:text-white px-3 py-1.5 rounded text-sm font-medium transition-all opacity-0 group-hover:opacity-100"
                                            >
                                                Review
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            {inboxCount > 10 && (
                                <div className="mt-4 pt-4 border-t border-grid-border">
                                    <button
                                        onClick={() => navigateTo('transactions')}
                                        className="w-full bg-neon-purple/10 hover:bg-neon-purple/20 text-neon-purple py-2 rounded text-sm font-medium transition-colors"
                                    >
                                        View All {inboxCount} Transactions →
                                    </button>
                                </div>
                            )}
                        </div>
                    )}
                </BentoBox>

                {/* Asset Watch - v3.0 Real Data */}
                <BentoBox title="Asset Watch" action={
                    <span className="text-xs text-gray-500">
                        {assetsV3.length > 0 ? `${assetsV3.length} Assets` : 'v3.0'}
                    </span>
                }>
                    {assetsV3.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-2 opacity-50">
                            <FileText size={32} />
                            <p className="text-xs">No assets tracked yet</p>
                            <p className="text-xs text-gray-600">Add assets to track net worth</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {assetsV3.slice(0, 5).map((asset: any) => {
                                const appreciation = asset.purchase_value
                                    ? ((asset.current_value - asset.purchase_value) / asset.purchase_value * 100).toFixed(1)
                                    : null;
                                const isPositive = appreciation && parseFloat(appreciation) > 0;

                                return (
                                    <div key={asset.id} className="flex justify-between items-center bg-white/5 p-3 rounded-lg hover:bg-white/10 transition-colors">
                                        <div>
                                            <span className="text-sm text-gray-300 block">{asset.name}</span>
                                            {appreciation && (
                                                <span className={`text-xs ${isPositive ? 'text-electric-green' : 'text-muted-red'}`}>
                                                    {isPositive ? '+' : ''}{appreciation}%
                                                </span>
                                            )}
                                        </div>
                                        <span className="font-mono text-white">${parseFloat(asset.current_value).toLocaleString()}</span>
                                    </div>
                                );
                            })}
                            {assetsV3.length > 5 && (
                                <button className="w-full text-xs text-gray-500 hover:text-neon-purple transition-colors py-2">
                                    +{assetsV3.length - 5} more assets
                                </button>
                            )}
                        </div>
                    )}
                </BentoBox>
            </div>

            {/* System Monitoring Dashboard */}
            <div className="mt-6">
                <SystemMonitor />
            </div>
        </div>
    );
};
