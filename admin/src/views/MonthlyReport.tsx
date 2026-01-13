import React, { useState, useEffect } from 'react';
import { BentoBox } from '../components/ui/BentoBox';
import {
    TrendingUp,
    TrendingDown,
    DollarSign,
    Download,
    Loader2,
    Receipt,
    Mail,
    Camera,
    FileCheck,
    Building2,
    AlertCircle,
    PiggyBank,
    Heart,
    Calendar
} from 'lucide-react';
import { api } from '../services/api';

interface Transaction {
    id: number;
    merchant: string;
    amount: number;
    category: string;
    date: string;
    status: string;
    source: 'document' | 'email' | 'manual';
    ai_confidence?: number;
}

interface Asset {
    id: number;
    name: string;
    type: string;
    value: number;
}

interface CanadianAccount {
    id: number;
    type: string;
    institution: string;
    holder: string;
    current_value: number;
    contribution_room: number;
}

interface GovBenefit {
    id: number;
    name: string;
    benefit_type: string;
    amount: number;
    frequency: string;
    next_payment_date: string;
}

interface MonthlyStats {
    total_income: number;
    total_expense: number;
    net_flow: number;
    transaction_count: number;
    top_categories: Array<{ category: string; amount: number; percentage: number }>;
    source_breakdown: { document: number; email: number; manual: number };
}

interface FinancialOverview {
    total_assets: number;
    total_liabilities: number;
    net_worth: number;
    savings_total: number;
    monthly_benefits: number;
}

export const MonthlyReport: React.FC = () => {
    const [loading, setLoading] = useState(true);
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [stats, setStats] = useState<MonthlyStats | null>(null);
    const [selectedMonth, setSelectedMonth] = useState(getCurrentMonth());
    const [filterSource, setFilterSource] = useState<string>('all');

    // New state for comprehensive financial data
    const [assets, setAssets] = useState<Asset[]>([]);
    const [canadianAccounts, setCanadianAccounts] = useState<CanadianAccount[]>([]);
    const [govBenefits, setGovBenefits] = useState<GovBenefit[]>([]);
    const [financialOverview, setFinancialOverview] = useState<FinancialOverview | null>(null);
    const [monthlyTrends, setMonthlyTrends] = useState<Array<{month: string, income: number, expense: number}>>([]);

    function getCurrentMonth(): string {
        const now = new Date();
        return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    }

    useEffect(() => {
        fetchAllFinancialData();
    }, [selectedMonth]);

    const fetchAllFinancialData = async () => {
        try {
            setLoading(true);

            // Fetch transactions
            const txnData = await api.getTransactions(0, 1000, selectedMonth);
            setTransactions(txnData);
            calculateStats(txnData);

            // Fetch assets
            const assetData = await api.getAssets();
            setAssets(assetData);

            // Fetch Canadian accounts (TFSA, RRSP, etc.)
            const accountData = await api.getCanadianAccounts();
            setCanadianAccounts(accountData);

            // Fetch government benefits
            const benefitData = await api.getGovBenefits();
            setGovBenefits(benefitData);

            // Calculate financial overview
            calculateFinancialOverview(assetData, accountData, benefitData);

            // Calculate monthly trends (last 6 months)
            await calculateMonthlyTrends();

        } catch (error) {
            console.error('Failed to fetch financial data:', error);
        } finally {
            setLoading(false);
        }
    };

    const calculateFinancialOverview = (
        assetData: Asset[],
        accountData: CanadianAccount[],
        benefitData: GovBenefit[]
    ) => {
        const total_assets = assetData.reduce((sum, a) => sum + a.value, 0);
        const savings_total = accountData.reduce((sum, a) => sum + a.current_value, 0);

        // Calculate monthly benefits
        const monthly_benefits = benefitData.reduce((sum, b) => {
            const amount = b.amount || 0;
            // Convert to monthly based on frequency
            if (b.frequency === 'MONTHLY' || b.frequency === 'monthly') return sum + amount;
            if (b.frequency === 'YEARLY' || b.frequency === 'yearly') return sum + (amount / 12);
            if (b.frequency === 'QUARTERLY' || b.frequency === 'quarterly') return sum + (amount / 3);
            return sum + amount; // Default to monthly
        }, 0);

        // For now, we don't have liabilities in v2.0 schema, so set to 0
        const total_liabilities = 0;

        setFinancialOverview({
            total_assets: total_assets + savings_total,
            total_liabilities,
            net_worth: total_assets + savings_total - total_liabilities,
            savings_total,
            monthly_benefits
        });
    };

    const calculateMonthlyTrends = async () => {
        try {
            const trends = [];
            const now = new Date();

            // Get last 6 months of data
            for (let i = 5; i >= 0; i--) {
                const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
                const monthStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

                try {
                    const monthTxns = await api.getTransactions(0, 1000, monthStr);
                    const income = monthTxns.filter((t: Transaction) => t.amount > 0).reduce((sum: number, t: Transaction) => sum + t.amount, 0);
                    const expense = Math.abs(monthTxns.filter((t: Transaction) => t.amount < 0).reduce((sum: number, t: Transaction) => sum + t.amount, 0));

                    trends.push({
                        month: date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short' }),
                        income,
                        expense
                    });
                } catch (err) {
                    // If month has no data, add zeros
                    trends.push({
                        month: date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short' }),
                        income: 0,
                        expense: 0
                    });
                }
            }

            setMonthlyTrends(trends);
        } catch (error) {
            console.error('Failed to calculate monthly trends:', error);
        }
    };

    const calculateStats = (txns: Transaction[]) => {
        const income = txns.filter(t => t.amount > 0).reduce((sum, t) => sum + t.amount, 0);
        const expense = Math.abs(txns.filter(t => t.amount < 0).reduce((sum, t) => sum + t.amount, 0));

        // Calculate category breakdown
        const categoryMap = new Map<string, number>();
        txns.forEach(t => {
            if (t.amount < 0) {
                const current = categoryMap.get(t.category) || 0;
                categoryMap.set(t.category, current + Math.abs(t.amount));
            }
        });

        const topCategories = Array.from(categoryMap.entries())
            .map(([category, amount]) => ({
                category,
                amount,
                percentage: (amount / expense) * 100
            }))
            .sort((a, b) => b.amount - a.amount)
            .slice(0, 5);

        // Source breakdown
        const sourceBreakdown = {
            document: txns.filter(t => t.source === 'document').length,
            email: txns.filter(t => t.source === 'email').length,
            manual: txns.filter(t => t.source === 'manual').length
        };

        setStats({
            total_income: income,
            total_expense: expense,
            net_flow: income - expense,
            transaction_count: txns.length,
            top_categories: topCategories,
            source_breakdown: sourceBreakdown
        });
    };

    const getFilteredTransactions = () => {
        if (filterSource === 'all') return transactions;
        return transactions.filter(t => t.source === filterSource);
    };

    const getSourceIcon = (source: string) => {
        switch (source) {
            case 'document': return <FileCheck size={16} className="text-neon-purple" />;
            case 'email': return <Mail size={16} className="text-blue-400" />;
            case 'manual': return <Camera size={16} className="text-electric-green" />;
            default: return <Receipt size={16} />;
        }
    };

    const getSourceLabel = (source: string) => {
        switch (source) {
            case 'document': return '文档扫描';
            case 'email': return '邮件导入';
            case 'manual': return '手动录入';
            default: return '未知';
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <Loader2 className="animate-spin text-neon-purple" size={48} />
            </div>
        );
    }

    const maxTrendValue = Math.max(...monthlyTrends.map(t => Math.max(t.income, t.expense)), 1);

    return (
        <div className="p-6 h-full overflow-y-auto">
            {/* Header */}
            <div className="mb-6 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-light text-white mb-1">
                        综合财务报表
                    </h1>
                    <p className="text-gray-500 text-sm">
                        资产、负债、储蓄、福利及月度收支全景视图
                    </p>
                </div>

                {/* Month Selector */}
                <div className="flex items-center gap-3">
                    <input
                        type="month"
                        value={selectedMonth}
                        onChange={(e) => setSelectedMonth(e.target.value)}
                        className="bg-finance-panel border border-grid-border rounded-lg px-4 py-2 text-white"
                    />
                    <button
                        onClick={() => api.exportTransactionsCSV()}
                        className="bg-electric-green/20 border border-electric-green text-electric-green px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-electric-green/30 transition-colors"
                    >
                        <Download size={18} />
                        导出报表
                    </button>
                </div>
            </div>

            {/* Financial Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
                <BentoBox className="bg-blue-500/10 border-blue-500/30">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-gray-400 text-sm mb-1">总资产</p>
                            <p className="text-2xl font-bold text-blue-400">
                                ${financialOverview?.total_assets.toLocaleString() || 0}
                            </p>
                        </div>
                        <Building2 className="text-blue-400" size={24} />
                    </div>
                </BentoBox>

                <BentoBox className="bg-red-500/10 border-red-500/30">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-gray-400 text-sm mb-1">总负债</p>
                            <p className="text-2xl font-bold text-red-400">
                                ${financialOverview?.total_liabilities.toLocaleString() || 0}
                            </p>
                        </div>
                        <AlertCircle className="text-red-400" size={24} />
                    </div>
                </BentoBox>

                <BentoBox className="bg-electric-green/10 border-electric-green/30">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-gray-400 text-sm mb-1">净资产</p>
                            <p className="text-2xl font-bold text-electric-green">
                                ${financialOverview?.net_worth.toLocaleString() || 0}
                            </p>
                        </div>
                        <DollarSign className="text-electric-green" size={24} />
                    </div>
                </BentoBox>

                <BentoBox className="bg-neon-purple/10 border-neon-purple/30">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-gray-400 text-sm mb-1">储蓄账户</p>
                            <p className="text-2xl font-bold text-neon-purple">
                                ${financialOverview?.savings_total.toLocaleString() || 0}
                            </p>
                        </div>
                        <PiggyBank className="text-neon-purple" size={24} />
                    </div>
                </BentoBox>

                <BentoBox className="bg-pink-500/10 border-pink-500/30">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-gray-400 text-sm mb-1">月度福利</p>
                            <p className="text-2xl font-bold text-pink-400">
                                ${financialOverview?.monthly_benefits.toLocaleString() || 0}
                            </p>
                        </div>
                        <Heart className="text-pink-400" size={24} />
                    </div>
                </BentoBox>
            </div>

            {/* Monthly Income/Expense Trends */}
            <div className="mb-6">
                <BentoBox>
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Calendar size={20} className="text-neon-purple" />
                        月度收支趋势 (近6个月)
                    </h3>
                    <div className="space-y-3">
                        {monthlyTrends.map((trend, idx) => (
                            <div key={idx} className="space-y-2">
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-gray-400 w-24">{trend.month}</span>
                                    <span className="text-electric-green font-mono">
                                        收入 ${trend.income.toLocaleString()}
                                    </span>
                                    <span className="text-red-400 font-mono">
                                        支出 ${trend.expense.toLocaleString()}
                                    </span>
                                    <span className={`font-mono font-semibold ${(trend.income - trend.expense) >= 0 ? 'text-electric-green' : 'text-red-400'}`}>
                                        净额 ${(trend.income - trend.expense).toLocaleString()}
                                    </span>
                                </div>
                                <div className="flex gap-2 h-8">
                                    <div className="flex-1 bg-gray-800 rounded-lg overflow-hidden flex">
                                        <div
                                            className="bg-electric-green/50 border-r border-electric-green"
                                            style={{ width: `${(trend.income / maxTrendValue) * 100}%` }}
                                        />
                                    </div>
                                    <div className="flex-1 bg-gray-800 rounded-lg overflow-hidden flex">
                                        <div
                                            className="bg-red-500/50 border-r border-red-500"
                                            style={{ width: `${(trend.expense / maxTrendValue) * 100}%` }}
                                        />
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </BentoBox>
            </div>

            {/* Assets and Savings Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                {/* Assets Breakdown */}
                <BentoBox>
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Building2 size={20} className="text-blue-400" />
                        资产明细
                    </h3>
                    {assets.length > 0 ? (
                        <div className="space-y-3">
                            {assets.map((asset) => (
                                <div key={asset.id} className="flex justify-between items-center p-3 bg-blue-500/5 border border-blue-500/20 rounded-lg">
                                    <div>
                                        <p className="text-white font-medium">{asset.name}</p>
                                        <p className="text-xs text-gray-500">{asset.type}</p>
                                    </div>
                                    <span className="text-blue-400 font-mono font-semibold">
                                        ${asset.value.toLocaleString()}
                                    </span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-500 text-center py-8">暂无资产记录</p>
                    )}
                </BentoBox>

                {/* Canadian Savings Accounts */}
                <BentoBox>
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <PiggyBank size={20} className="text-neon-purple" />
                        储蓄计划 (TFSA/RRSP/RESP)
                    </h3>
                    {canadianAccounts.length > 0 ? (
                        <div className="space-y-3">
                            {canadianAccounts.map((account) => (
                                <div key={account.id} className="p-3 bg-neon-purple/5 border border-neon-purple/20 rounded-lg">
                                    <div className="flex justify-between items-start mb-2">
                                        <div>
                                            <p className="text-white font-medium">{account.type}</p>
                                            <p className="text-xs text-gray-500">{account.institution} - {account.holder}</p>
                                        </div>
                                        <span className="text-neon-purple font-mono font-semibold">
                                            ${account.current_value.toLocaleString()}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center text-xs">
                                        <span className="text-gray-500">可用额度</span>
                                        <span className="text-electric-green font-mono">
                                            ${account.contribution_room.toLocaleString()}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-500 text-center py-8">暂无储蓄账户</p>
                    )}
                </BentoBox>
            </div>

            {/* Government Benefits */}
            <div className="mb-6">
                <BentoBox>
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                        <Heart size={20} className="text-pink-400" />
                        政府福利及使用情况
                    </h3>
                    {govBenefits.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {govBenefits.map((benefit) => (
                                <div key={benefit.id} className="p-4 bg-pink-500/5 border border-pink-500/20 rounded-lg">
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex-1">
                                            <p className="text-white font-medium text-sm">{benefit.name}</p>
                                            <p className="text-xs text-gray-500 mt-1">{benefit.benefit_type}</p>
                                        </div>
                                    </div>
                                    <div className="mt-3 pt-3 border-t border-pink-500/20">
                                        <div className="flex justify-between items-center">
                                            <span className="text-xs text-gray-400">金额 ({benefit.frequency})</span>
                                            <span className="text-pink-400 font-mono font-semibold">
                                                ${benefit.amount.toLocaleString()}
                                            </span>
                                        </div>
                                        {benefit.next_payment_date && (
                                            <div className="flex justify-between items-center mt-2">
                                                <span className="text-xs text-gray-400">下次发放</span>
                                                <span className="text-xs text-gray-300">
                                                    {new Date(benefit.next_payment_date).toLocaleDateString('zh-CN')}
                                                </span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-500 text-center py-8">暂无福利记录</p>
                    )}
                </BentoBox>
            </div>

            {/* Current Month Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <BentoBox className="bg-electric-green/10 border-electric-green/30">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-gray-400 text-sm mb-1">本月收入</p>
                            <p className="text-2xl font-bold text-electric-green">
                                +${stats?.total_income.toLocaleString() || 0}
                            </p>
                        </div>
                        <TrendingUp className="text-electric-green" size={24} />
                    </div>
                </BentoBox>

                <BentoBox className="bg-red-500/10 border-red-500/30">
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-gray-400 text-sm mb-1">本月支出</p>
                            <p className="text-2xl font-bold text-red-400">
                                -${stats?.total_expense.toLocaleString() || 0}
                            </p>
                        </div>
                        <TrendingDown className="text-red-400" size={24} />
                    </div>
                </BentoBox>

                <BentoBox className={`${(stats?.net_flow || 0) >= 0 ? 'bg-electric-green/10 border-electric-green/30' : 'bg-red-500/10 border-red-500/30'}`}>
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-gray-400 text-sm mb-1">净现金流</p>
                            <p className={`text-2xl font-bold ${(stats?.net_flow || 0) >= 0 ? 'text-electric-green' : 'text-red-400'}`}>
                                {(stats?.net_flow || 0) >= 0 ? '+' : ''}${stats?.net_flow.toLocaleString() || 0}
                            </p>
                        </div>
                        <DollarSign className={(stats?.net_flow || 0) >= 0 ? 'text-electric-green' : 'text-red-400'} size={24} />
                    </div>
                </BentoBox>

                <BentoBox>
                    <div className="flex items-start justify-between">
                        <div>
                            <p className="text-gray-400 text-sm mb-1">交易笔数</p>
                            <p className="text-2xl font-bold text-white">
                                {stats?.transaction_count || 0}
                            </p>
                        </div>
                        <Receipt className="text-neon-purple" size={24} />
                    </div>
                </BentoBox>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                {/* Category Breakdown */}
                <BentoBox>
                    <h3 className="text-lg font-semibold text-white mb-4">本月支出分类占比</h3>
                    <div className="space-y-3">
                        {stats?.top_categories.map((cat, idx) => (
                            <div key={idx}>
                                <div className="flex justify-between items-center mb-1">
                                    <span className="text-sm text-gray-300">{cat.category}</span>
                                    <span className="text-sm text-white font-mono">
                                        ${cat.amount.toLocaleString()} ({cat.percentage.toFixed(1)}%)
                                    </span>
                                </div>
                                <div className="w-full bg-gray-800 rounded-full h-2">
                                    <div
                                        className="bg-gradient-to-r from-neon-purple to-electric-green h-2 rounded-full transition-all"
                                        style={{ width: `${cat.percentage}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </BentoBox>

                {/* Source Breakdown */}
                <BentoBox>
                    <h3 className="text-lg font-semibold text-white mb-4">数据来源分布</h3>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 bg-neon-purple/10 border border-neon-purple/30 rounded-lg">
                            <div className="flex items-center gap-3">
                                <FileCheck size={20} className="text-neon-purple" />
                                <span className="text-white">文档扫描</span>
                            </div>
                            <span className="text-xl font-bold text-neon-purple">
                                {stats?.source_breakdown.document || 0}
                            </span>
                        </div>

                        <div className="flex items-center justify-between p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                            <div className="flex items-center gap-3">
                                <Mail size={20} className="text-blue-400" />
                                <span className="text-white">邮件导入</span>
                            </div>
                            <span className="text-xl font-bold text-blue-400">
                                {stats?.source_breakdown.email || 0}
                            </span>
                        </div>

                        <div className="flex items-center justify-between p-3 bg-electric-green/10 border border-electric-green/30 rounded-lg">
                            <div className="flex items-center gap-3">
                                <Camera size={20} className="text-electric-green" />
                                <span className="text-white">手动录入</span>
                            </div>
                            <span className="text-xl font-bold text-electric-green">
                                {stats?.source_breakdown.manual || 0}
                            </span>
                        </div>
                    </div>
                </BentoBox>
            </div>

            {/* Transaction Details Table */}
            <BentoBox>
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold text-white">本月交易明细</h3>

                    {/* Source Filter */}
                    <div className="flex gap-2">
                        {['all', 'document', 'email', 'manual'].map((source) => (
                            <button
                                key={source}
                                onClick={() => setFilterSource(source)}
                                className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                                    filterSource === source
                                        ? 'bg-neon-purple text-white'
                                        : 'bg-finance-black text-gray-400 hover:text-white'
                                }`}
                            >
                                {source === 'all' ? '全部' : getSourceLabel(source)}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-grid-border">
                                <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">日期</th>
                                <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">商户</th>
                                <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">分类</th>
                                <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">来源</th>
                                <th className="text-right py-3 px-4 text-gray-400 font-medium text-sm">金额</th>
                            </tr>
                        </thead>
                        <tbody>
                            {getFilteredTransactions().map((txn) => (
                                <tr key={txn.id} className="border-b border-grid-border/50 hover:bg-white/5 transition-colors">
                                    <td className="py-3 px-4 text-sm text-gray-300">
                                        {new Date(txn.date).toLocaleDateString('zh-CN')}
                                    </td>
                                    <td className="py-3 px-4 text-sm text-white">{txn.merchant}</td>
                                    <td className="py-3 px-4">
                                        <span className="px-2 py-1 bg-neon-purple/20 text-neon-purple rounded text-xs">
                                            {txn.category}
                                        </span>
                                    </td>
                                    <td className="py-3 px-4">
                                        <div className="flex items-center gap-2">
                                            {getSourceIcon(txn.source)}
                                            <span className="text-xs text-gray-400">
                                                {getSourceLabel(txn.source)}
                                            </span>
                                        </div>
                                    </td>
                                    <td className={`py-3 px-4 text-right font-mono font-semibold ${
                                        txn.amount >= 0 ? 'text-electric-green' : 'text-red-400'
                                    }`}>
                                        {txn.amount >= 0 ? '+' : ''}${Math.abs(txn.amount).toLocaleString()}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    {getFilteredTransactions().length === 0 && (
                        <div className="text-center py-12 text-gray-500">
                            暂无交易数据
                        </div>
                    )}
                </div>
            </BentoBox>
        </div>
    );
};
