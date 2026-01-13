import React from 'react';
import { Edit2, Trash2, TrendingUp, TrendingDown } from 'lucide-react';
import { motion } from 'framer-motion';

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

interface BudgetCardProps {
    budget: BudgetStatus;
    onEdit: (id: number) => void;
    onDelete: (id: number) => void;
}

export const BudgetCard: React.FC<BudgetCardProps> = ({ budget, onEdit, onDelete }) => {
    const getStatusColor = () => {
        if (budget.is_over_budget) return 'bg-muted-red';
        if (budget.is_near_limit) return 'bg-signal-orange';
        return 'bg-electric-green';
    };

    const getTextColor = () => {
        if (budget.is_over_budget) return 'text-muted-red';
        if (budget.is_near_limit) return 'text-signal-orange';
        return 'text-electric-green';
    };

    const getStatusText = () => {
        if (budget.is_over_budget) return '超支';
        if (budget.is_near_limit) return '接近限额';
        return '正常';
    };

    const getStatusIcon = () => {
        if (budget.is_over_budget || budget.is_near_limit) {
            return <TrendingDown className="w-4 h-4 inline mr-1" />;
        }
        return <TrendingUp className="w-4 h-4 inline mr-1" />;
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="bg-finance-panel border border-grid-border rounded-2xl p-6 hover:border-neon-purple/30 transition-all"
        >
            {/* Header */}
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-lg font-semibold text-white mb-1">{budget.category}</h3>
                    <p className="text-xs text-gray-500">Monthly Budget</p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => onEdit(budget.id)}
                        className="p-2 hover:bg-finance-black rounded-lg transition-colors group"
                        title="Edit Budget"
                    >
                        <Edit2 className="w-4 h-4 text-gray-400 group-hover:text-neon-purple" />
                    </button>
                    <button
                        onClick={() => onDelete(budget.id)}
                        className="p-2 hover:bg-finance-black rounded-lg transition-colors group"
                        title="Delete Budget"
                    >
                        <Trash2 className="w-4 h-4 text-gray-400 group-hover:text-muted-red" />
                    </button>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-3">
                <div className="w-full bg-finance-black rounded-full h-3 overflow-hidden">
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(budget.percentage_used, 100)}%` }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                        className={`${getStatusColor()} h-3 rounded-full relative`}
                    >
                        {/* Glow effect */}
                        <div className={`absolute inset-0 ${getStatusColor()} opacity-50 blur-sm`}></div>
                    </motion.div>
                </div>
            </div>

            {/* Amount Details */}
            <div className="flex justify-between items-center mb-3">
                <div>
                    <p className="text-2xl font-bold font-mono text-white">
                        ${budget.current_spent.toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500">
                        of ${budget.monthly_limit.toFixed(2)}
                    </p>
                </div>
                <div className="text-right">
                    <p className={`text-3xl font-bold font-mono ${getTextColor()}`}>
                        {budget.percentage_used.toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-500">Used</p>
                </div>
            </div>

            {/* Divider */}
            <div className="border-t border-grid-border my-4"></div>

            {/* Status and Remaining */}
            <div className="flex justify-between items-center">
                <div>
                    <p className="text-sm text-gray-400">Remaining</p>
                    <p className={`text-lg font-semibold font-mono ${
                        budget.remaining > 0 ? 'text-electric-green' : 'text-muted-red'
                    }`}>
                        ${Math.abs(budget.remaining).toFixed(2)}
                    </p>
                </div>
                <div className="text-right">
                    <p className={`text-sm font-medium ${getTextColor()} flex items-center`}>
                        {getStatusIcon()}
                        {getStatusText()}
                    </p>
                    <p className="text-xs text-gray-500">
                        Alert at {budget.alert_threshold}%
                    </p>
                </div>
            </div>

            {/* Warning Banner (if over budget or near limit) */}
            {(budget.is_over_budget || budget.is_near_limit) && (
                <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className={`mt-4 p-3 rounded-lg border ${
                        budget.is_over_budget
                            ? 'bg-muted-red/10 border-muted-red/30'
                            : 'bg-signal-orange/10 border-signal-orange/30'
                    }`}
                >
                    <p className={`text-sm ${
                        budget.is_over_budget ? 'text-muted-red' : 'text-signal-orange'
                    }`}>
                        {budget.is_over_budget
                            ? `⚠️ Over budget by $${(-budget.remaining).toFixed(2)}`
                            : `⚠️ ${(100 - budget.percentage_used).toFixed(1)}% remaining`
                        }
                    </p>
                </motion.div>
            )}
        </motion.div>
    );
};
