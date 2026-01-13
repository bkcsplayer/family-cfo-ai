import React, { useState, useEffect } from 'react';
import { BudgetCard } from '../components/BudgetCard';
import { BentoBox } from '../components/ui/BentoBox';
import { api } from '../services/api';
import { Plus, AlertCircle, RefreshCw, Download, TrendingUp, DollarSign } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface BudgetStatus {
    id: number;
    category: string;
    monthly_limit: number;
    current_spent: number;
    remaining: number;
    percentage_used: number;
    alert_threshold: number;
    is_over_budget: boolean;
    is_near_limit: boolean;
}

export const BudgetManager: React.FC = () => {
    const [budgets, setBudgets] = useState<BudgetStatus[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [currentEditId, setCurrentEditId] = useState<number | null>(null);
    const [formData, setFormData] = useState({
        category: '',
        monthly_limit: '',
        alert_threshold: '90',
    });

    // Load budgets
    const loadBudgets = async () => {
        try {
            setLoading(true);
            const data = await api.getBudgetStatus();
            setBudgets(data);
        } catch (error) {
            console.error('Failed to load budgets:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadBudgets();
    }, []);

    // Calculate summary stats
    const totalBudgets = budgets.length;
    const overBudgetCount = budgets.filter(b => b.is_over_budget).length;
    const nearLimitCount = budgets.filter(b => b.is_near_limit && !b.is_over_budget).length;
    const totalBudgeted = budgets.reduce((sum, b) => sum + b.monthly_limit, 0);
    const totalSpent = budgets.reduce((sum, b) => sum + b.current_spent, 0);

    // Handle create budget
    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.createBudget({
                category: formData.category,
                monthly_limit: parseFloat(formData.monthly_limit),
                alert_threshold: parseFloat(formData.alert_threshold),
            });
            setShowCreateModal(false);
            setFormData({ category: '', monthly_limit: '', alert_threshold: '90' });
            loadBudgets();
        } catch (error) {
            console.error('Failed to create budget:', error);
            alert('Failed to create budget. Please try again.');
        }
    };

    // Handle edit budget
    const handleEdit = (id: number) => {
        const budget = budgets.find(b => b.id === id);
        if (budget) {
            setCurrentEditId(id);
            setFormData({
                category: budget.category,
                monthly_limit: budget.monthly_limit.toString(),
                alert_threshold: budget.alert_threshold.toString(),
            });
            setShowEditModal(true);
        }
    };

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!currentEditId) return;

        try {
            await api.updateBudget(currentEditId, {
                monthly_limit: parseFloat(formData.monthly_limit),
                alert_threshold: parseFloat(formData.alert_threshold),
            });
            setShowEditModal(false);
            setCurrentEditId(null);
            setFormData({ category: '', monthly_limit: '', alert_threshold: '90' });
            loadBudgets();
        } catch (error) {
            console.error('Failed to update budget:', error);
            alert('Failed to update budget. Please try again.');
        }
    };

    // Handle delete budget
    const handleDelete = async (id: number) => {
        const budget = budgets.find(b => b.id === id);
        if (!budget) return;

        if (window.confirm(`Are you sure you want to delete the budget for "${budget.category}"?`)) {
            try {
                await api.deleteBudget(id);
                loadBudgets();
            } catch (error) {
                console.error('Failed to delete budget:', error);
                alert('Failed to delete budget. Please try again.');
            }
        }
    };

    // Handle export
    const handleExport = async () => {
        try {
            await api.exportBudgetsExcel();
        } catch (error) {
            console.error('Failed to export budgets:', error);
            alert('Failed to export budgets. Please try again.');
        }
    };

    return (
        <div className="p-6 h-full overflow-y-auto">
            {/* Header */}
            <header className="mb-6">
                <div className="flex justify-between items-start mb-2">
                    <div>
                        <h1 className="text-3xl font-light text-white mb-1 tracking-tight">
                            Budget <span className="text-gray-500">Manager</span>
                        </h1>
                        <p className="text-gray-500 text-sm">Track and manage monthly budget limits</p>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={loadBudgets}
                            className="px-4 py-2 bg-finance-panel border border-grid-border rounded-lg hover:border-neon-purple/50 transition-all flex items-center gap-2 text-white"
                        >
                            <RefreshCw className="w-4 h-4" />
                            Refresh
                        </button>
                        <button
                            onClick={handleExport}
                            className="px-4 py-2 bg-finance-panel border border-grid-border rounded-lg hover:border-electric-green/50 transition-all flex items-center gap-2 text-white"
                        >
                            <Download className="w-4 h-4" />
                            Export
                        </button>
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="px-4 py-2 bg-neon-purple text-white rounded-lg hover:bg-neon-purple/80 transition-all flex items-center gap-2 font-medium"
                        >
                            <Plus className="w-4 h-4" />
                            Create Budget
                        </button>
                    </div>
                </div>
            </header>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <BentoBox>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-gray-500 text-sm mb-1">Total Budgets</p>
                            <p className="text-3xl font-bold font-mono text-white">{totalBudgets}</p>
                        </div>
                        <DollarSign className="w-10 h-10 text-neon-purple opacity-50" />
                    </div>
                </BentoBox>

                <BentoBox>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-gray-500 text-sm mb-1">Total Budgeted</p>
                            <p className="text-2xl font-bold font-mono text-white">${totalBudgeted.toFixed(2)}</p>
                        </div>
                        <TrendingUp className="w-10 h-10 text-electric-green opacity-50" />
                    </div>
                </BentoBox>

                <BentoBox>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-gray-500 text-sm mb-1">Total Spent</p>
                            <p className="text-2xl font-bold font-mono text-white">${totalSpent.toFixed(2)}</p>
                            <p className="text-xs text-gray-500 mt-1">
                                {totalBudgeted > 0 ? ((totalSpent / totalBudgeted) * 100).toFixed(1) : 0}% used
                            </p>
                        </div>
                        <DollarSign className="w-10 h-10 text-signal-orange opacity-50" />
                    </div>
                </BentoBox>

                <BentoBox>
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-gray-500 text-sm mb-1">Alerts</p>
                            <p className="text-3xl font-bold font-mono text-muted-red">{overBudgetCount}</p>
                            <p className="text-xs text-gray-500 mt-1">
                                {nearLimitCount} near limit
                            </p>
                        </div>
                        <AlertCircle className="w-10 h-10 text-muted-red opacity-50" />
                    </div>
                </BentoBox>
            </div>

            {/* Budget Cards Grid */}
            {loading ? (
                <div className="flex items-center justify-center h-64">
                    <div className="text-gray-500">Loading budgets...</div>
                </div>
            ) : budgets.length === 0 ? (
                <BentoBox>
                    <div className="text-center py-12">
                        <DollarSign className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-white mb-2">No budgets yet</h3>
                        <p className="text-gray-500 mb-4">Create your first budget to start tracking spending limits</p>
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="px-6 py-3 bg-neon-purple text-white rounded-lg hover:bg-neon-purple/80 transition-all inline-flex items-center gap-2"
                        >
                            <Plus className="w-5 h-5" />
                            Create Your First Budget
                        </button>
                    </div>
                </BentoBox>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                    {budgets.map((budget) => (
                        <BudgetCard
                            key={budget.id}
                            budget={budget}
                            onEdit={handleEdit}
                            onDelete={handleDelete}
                        />
                    ))}
                </div>
            )}

            {/* Create Budget Modal */}
            <AnimatePresence>
                {showCreateModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                            onClick={() => setShowCreateModal(false)}
                        />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-finance-panel border border-grid-border rounded-2xl p-6 max-w-md w-full relative z-10 shadow-2xl"
                        >
                            <h3 className="text-2xl font-bold text-white mb-4">Create New Budget</h3>
                            <form onSubmit={handleCreate}>
                                <div className="mb-4">
                                    <label className="block text-sm text-gray-400 mb-2">Category</label>
                                    <input
                                        type="text"
                                        value={formData.category}
                                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                        className="w-full bg-finance-black border border-grid-border rounded-lg px-4 py-2 text-white focus:outline-none focus:border-neon-purple"
                                        placeholder="e.g., Food - Restaurants"
                                        required
                                    />
                                </div>
                                <div className="mb-4">
                                    <label className="block text-sm text-gray-400 mb-2">Monthly Limit ($)</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={formData.monthly_limit}
                                        onChange={(e) => setFormData({ ...formData, monthly_limit: e.target.value })}
                                        className="w-full bg-finance-black border border-grid-border rounded-lg px-4 py-2 text-white focus:outline-none focus:border-neon-purple"
                                        placeholder="500.00"
                                        required
                                    />
                                </div>
                                <div className="mb-6">
                                    <label className="block text-sm text-gray-400 mb-2">Alert Threshold (%)</label>
                                    <input
                                        type="number"
                                        step="1"
                                        value={formData.alert_threshold}
                                        onChange={(e) => setFormData({ ...formData, alert_threshold: e.target.value })}
                                        className="w-full bg-finance-black border border-grid-border rounded-lg px-4 py-2 text-white focus:outline-none focus:border-neon-purple"
                                        placeholder="90"
                                        required
                                    />
                                    <p className="text-xs text-gray-500 mt-1">Alert when spending reaches this percentage</p>
                                </div>
                                <div className="flex gap-3">
                                    <button
                                        type="button"
                                        onClick={() => setShowCreateModal(false)}
                                        className="flex-1 px-4 py-2 bg-finance-black border border-grid-border rounded-lg text-white hover:border-gray-600 transition-all"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="flex-1 px-4 py-2 bg-neon-purple text-white rounded-lg hover:bg-neon-purple/80 transition-all font-medium"
                                    >
                                        Create Budget
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* Edit Budget Modal */}
            <AnimatePresence>
                {showEditModal && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                            onClick={() => setShowEditModal(false)}
                        />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-finance-panel border border-grid-border rounded-2xl p-6 max-w-md w-full relative z-10 shadow-2xl"
                        >
                            <h3 className="text-2xl font-bold text-white mb-4">Edit Budget</h3>
                            <form onSubmit={handleUpdate}>
                                <div className="mb-4">
                                    <label className="block text-sm text-gray-400 mb-2">Category</label>
                                    <input
                                        type="text"
                                        value={formData.category}
                                        disabled
                                        className="w-full bg-finance-black/50 border border-grid-border rounded-lg px-4 py-2 text-gray-500"
                                    />
                                    <p className="text-xs text-gray-500 mt-1">Category cannot be changed</p>
                                </div>
                                <div className="mb-4">
                                    <label className="block text-sm text-gray-400 mb-2">Monthly Limit ($)</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={formData.monthly_limit}
                                        onChange={(e) => setFormData({ ...formData, monthly_limit: e.target.value })}
                                        className="w-full bg-finance-black border border-grid-border rounded-lg px-4 py-2 text-white focus:outline-none focus:border-neon-purple"
                                        required
                                    />
                                </div>
                                <div className="mb-6">
                                    <label className="block text-sm text-gray-400 mb-2">Alert Threshold (%)</label>
                                    <input
                                        type="number"
                                        step="1"
                                        value={formData.alert_threshold}
                                        onChange={(e) => setFormData({ ...formData, alert_threshold: e.target.value })}
                                        className="w-full bg-finance-black border border-grid-border rounded-lg px-4 py-2 text-white focus:outline-none focus:border-neon-purple"
                                        required
                                    />
                                </div>
                                <div className="flex gap-3">
                                    <button
                                        type="button"
                                        onClick={() => setShowEditModal(false)}
                                        className="flex-1 px-4 py-2 bg-finance-black border border-grid-border rounded-lg text-white hover:border-gray-600 transition-all"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="flex-1 px-4 py-2 bg-neon-purple text-white rounded-lg hover:bg-neon-purple/80 transition-all font-medium"
                                    >
                                        Update Budget
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};
