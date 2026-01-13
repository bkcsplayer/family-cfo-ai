import React, { useState, useEffect } from 'react';
import { Activity, Database, Mail, Cpu, Loader2, Zap, ArrowRight, Clock, Inbox, TrendingUp } from 'lucide-react';
import { api } from '../services/api';

export const SystemMonitor: React.FC = () => {
    const [systemStatus, setSystemStatus] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const data = await api.getSystemStatus();
                setSystemStatus(data);
            } catch (error) {
                console.error('Failed to fetch system status:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 10000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="bg-gradient-to-br from-finance-panel to-finance-black border border-grid-border p-8 rounded-2xl">
                <div className="flex items-center justify-center py-12">
                    <Loader2 className="animate-spin text-neon-purple" size={40} />
                </div>
            </div>
        );
    }

    if (!systemStatus) {
        return null;
    }

    const services = systemStatus.services || {};
    const aiUsage = systemStatus.ai_usage || {};
    const sources = systemStatus.transaction_sources_24h || {};
    const queue = systemStatus.processing_queue || {};

    // Calculate percentages for visual bars
    const totalSources = (sources.mobile || 0) + (sources.email || 0) + (sources.manual || 0);
    const mobilePercent = totalSources > 0 ? ((sources.mobile || 0) / totalSources) * 100 : 33;
    const emailPercent = totalSources > 0 ? ((sources.email || 0) / totalSources) * 100 : 33;
    const manualPercent = totalSources > 0 ? ((sources.manual || 0) / totalSources) * 100 : 33;

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-2 h-8 bg-gradient-to-b from-neon-purple to-electric-green rounded-full" />
                    <h2 className="text-lg font-semibold text-white">System Control Center</h2>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500 bg-finance-panel px-3 py-1.5 rounded-full border border-grid-border">
                    <Clock size={12} />
                    <span>Live • {new Date(systemStatus.timestamp).toLocaleTimeString()}</span>
                </div>
            </div>

            {/* Main Grid - 2 Column Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Left Column - Services & AI */}
                <div className="space-y-4">
                    {/* Services Status - Compact Row */}
                    <div className="bg-gradient-to-br from-finance-panel to-black/50 border border-grid-border p-5 rounded-2xl">
                        <div className="flex items-center gap-2 mb-4">
                            <Zap size={16} className="text-electric-green" />
                            <span className="text-sm font-medium text-gray-400 uppercase tracking-wider">Services</span>
                        </div>
                        <div className="flex gap-4">
                            {/* Database Status */}
                            <div className={`flex-1 p-4 rounded-xl border ${services.database?.healthy ? 'bg-electric-green/5 border-electric-green/20' : 'bg-red-500/5 border-red-500/20'}`}>
                                <div className="flex items-center gap-3">
                                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${services.database?.healthy ? 'bg-electric-green/10' : 'bg-red-500/10'}`}>
                                        <Database size={20} className={services.database?.healthy ? 'text-electric-green' : 'text-red-500'} />
                                    </div>
                                    <div>
                                        <div className="text-sm font-medium text-white">Database</div>
                                        <div className={`text-xs ${services.database?.healthy ? 'text-electric-green' : 'text-red-500'}`}>
                                            {services.database?.healthy ? '● Online' : '● Offline'}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Email Status */}
                            <div className={`flex-1 p-4 rounded-xl border ${services.email?.enabled ? 'bg-blue-500/5 border-blue-500/20' : 'bg-gray-800/50 border-gray-700'}`}>
                                <div className="flex items-center gap-3">
                                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${services.email?.enabled ? 'bg-blue-500/10' : 'bg-gray-800'}`}>
                                        <Mail size={20} className={services.email?.enabled ? 'text-blue-400' : 'text-gray-600'} />
                                    </div>
                                    <div>
                                        <div className="text-sm font-medium text-white">Email</div>
                                        <div className={`text-xs ${services.email?.enabled ? 'text-blue-400' : 'text-gray-600'}`}>
                                            {services.email?.imap_listener ? '● Listening' : services.email?.enabled ? '● Ready' : '● Disabled'}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* AI Status */}
                            <div className={`flex-1 p-4 rounded-xl border ${services.ai?.enabled ? 'bg-neon-purple/5 border-neon-purple/20' : 'bg-gray-800/50 border-gray-700'}`}>
                                <div className="flex items-center gap-3">
                                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${services.ai?.enabled ? 'bg-neon-purple/10' : 'bg-gray-800'}`}>
                                        <Cpu size={20} className={services.ai?.enabled ? 'text-neon-purple' : 'text-gray-600'} />
                                    </div>
                                    <div>
                                        <div className="text-sm font-medium text-white">AI Engine</div>
                                        <div className={`text-xs ${services.ai?.enabled ? 'text-neon-purple' : 'text-gray-600'}`}>
                                            {services.ai?.enabled ? '● Active' : '● Offline'}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* AI Token Usage - Modern Card */}
                    {services.ai?.enabled && (
                        <div className="bg-gradient-to-br from-neon-purple/10 via-finance-panel to-black/50 border border-neon-purple/20 p-5 rounded-2xl relative overflow-hidden">
                            {/* Background decoration */}
                            <div className="absolute -right-10 -top-10 w-40 h-40 bg-neon-purple/5 rounded-full blur-3xl" />

                            <div className="relative">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-2">
                                        <Activity size={16} className="text-neon-purple" />
                                        <span className="text-sm font-medium text-gray-400 uppercase tracking-wider">AI Usage</span>
                                    </div>
                                    <span className="text-xs text-gray-600 bg-black/30 px-2 py-1 rounded-md">
                                        {services.ai?.model?.split('/').pop() || 'Claude'}
                                    </span>
                                </div>

                                {/* Usage Stats Grid */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-black/30 rounded-xl p-4 border border-neon-purple/10">
                                        <div className="text-xs text-gray-500 mb-1">Today</div>
                                        <div className="flex items-baseline gap-2">
                                            <span className="text-3xl font-mono font-bold text-neon-purple">
                                                {aiUsage.today_requests || 0}
                                            </span>
                                            <span className="text-xs text-gray-500">requests</span>
                                        </div>
                                        <div className="text-xs text-gray-600 mt-1 font-mono">
                                            {(aiUsage.today_tokens || 0).toLocaleString()} tokens
                                        </div>
                                    </div>
                                    <div className="bg-black/30 rounded-xl p-4 border border-grid-border">
                                        <div className="text-xs text-gray-500 mb-1">All Time</div>
                                        <div className="flex items-baseline gap-2">
                                            <span className="text-3xl font-mono font-bold text-white">
                                                {aiUsage.total_requests || 0}
                                            </span>
                                            <span className="text-xs text-gray-500">requests</span>
                                        </div>
                                        <div className="text-xs text-gray-600 mt-1 font-mono">
                                            {(aiUsage.total_tokens || 0).toLocaleString()} tokens
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right Column - Transaction Sources & Queue */}
                <div className="space-y-4">
                    {/* Transaction Sources - Redesigned */}
                    <div className="bg-gradient-to-br from-finance-panel to-black/50 border border-grid-border p-5 rounded-2xl">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                                <Inbox size={16} className="text-blue-400" />
                                <span className="text-sm font-medium text-gray-400 uppercase tracking-wider">Transaction Sources</span>
                            </div>
                            <span className="text-xs text-gray-600">Last 24h</span>
                        </div>

                        {/* Total Counter */}
                        <div className="text-center mb-6">
                            <div className="text-5xl font-mono font-bold text-white mb-1">
                                {sources.total || 0}
                            </div>
                            <div className="text-xs text-gray-500">Total Transactions</div>
                        </div>

                        {/* Source Breakdown - Horizontal Bars */}
                        <div className="space-y-3">
                            {/* Mobile */}
                            <div className="flex items-center gap-3">
                                <div className="w-16 text-right">
                                    <span className="text-sm font-mono text-neon-purple">{sources.mobile || 0}</span>
                                </div>
                                <div className="flex-1 h-8 bg-black/30 rounded-lg overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-neon-purple/80 to-neon-purple/40 rounded-lg flex items-center justify-end pr-3 transition-all duration-500"
                                        style={{ width: `${Math.max(mobilePercent, 5)}%` }}
                                    >
                                        <span className="text-xs text-white/80">📱 Mobile</span>
                                    </div>
                                </div>
                            </div>

                            {/* Email */}
                            <div className="flex items-center gap-3">
                                <div className="w-16 text-right">
                                    <span className="text-sm font-mono text-blue-400">{sources.email || 0}</span>
                                </div>
                                <div className="flex-1 h-8 bg-black/30 rounded-lg overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-blue-500/80 to-blue-500/40 rounded-lg flex items-center justify-end pr-3 transition-all duration-500"
                                        style={{ width: `${Math.max(emailPercent, 5)}%` }}
                                    >
                                        <span className="text-xs text-white/80">📧 Email</span>
                                    </div>
                                </div>
                            </div>

                            {/* Manual */}
                            <div className="flex items-center gap-3">
                                <div className="w-16 text-right">
                                    <span className="text-sm font-mono text-gray-400">{sources.manual || 0}</span>
                                </div>
                                <div className="flex-1 h-8 bg-black/30 rounded-lg overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-gray-500/80 to-gray-500/40 rounded-lg flex items-center justify-end pr-3 transition-all duration-500"
                                        style={{ width: `${Math.max(manualPercent, 5)}%` }}
                                    >
                                        <span className="text-xs text-white/80">✏️ Manual</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Processing Queue - Compact */}
                    <div className="bg-gradient-to-br from-yellow-500/5 via-finance-panel to-black/50 border border-yellow-500/20 p-5 rounded-2xl">
                        <div className="flex items-center gap-2 mb-4">
                            <TrendingUp size={16} className="text-yellow-400" />
                            <span className="text-sm font-medium text-gray-400 uppercase tracking-wider">Processing Queue</span>
                        </div>

                        <div className="flex items-center justify-between">
                            {/* Pending */}
                            <div className="text-center flex-1">
                                <div className="w-16 h-16 mx-auto mb-2 rounded-2xl bg-yellow-500/10 border border-yellow-500/20 flex items-center justify-center">
                                    <span className="text-2xl font-mono font-bold text-yellow-400">{queue.pending || 0}</span>
                                </div>
                                <div className="text-xs text-gray-500">Pending</div>
                            </div>

                            <ArrowRight size={20} className="text-gray-700" />

                            {/* Draft */}
                            <div className="text-center flex-1">
                                <div className="w-16 h-16 mx-auto mb-2 rounded-2xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center">
                                    <span className="text-2xl font-mono font-bold text-orange-400">{queue.draft || 0}</span>
                                </div>
                                <div className="text-xs text-gray-500">Draft</div>
                            </div>

                            <ArrowRight size={20} className="text-gray-700" />

                            {/* Total */}
                            <div className="text-center flex-1">
                                <div className="w-16 h-16 mx-auto mb-2 rounded-2xl bg-gray-800 border border-gray-700 flex items-center justify-center">
                                    <span className="text-2xl font-mono font-bold text-white">{queue.total_waiting || 0}</span>
                                </div>
                                <div className="text-xs text-gray-500">Total</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
