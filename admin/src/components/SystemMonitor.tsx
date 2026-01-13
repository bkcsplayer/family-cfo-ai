import React, { useState, useEffect } from 'react';
import { Activity, Database, Mail, Cpu, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
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
        // Refresh every 10 seconds
        const interval = setInterval(fetchStatus, 10000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="bg-finance-panel border border-grid-border p-6 rounded-xl">
                <div className="flex items-center justify-center py-8">
                    <Loader2 className="animate-spin text-neon-purple" size={32} />
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

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-sm font-medium uppercase tracking-wider text-gray-400">System Monitor</h2>
                <div className="text-xs text-gray-500">
                    Last updated: {new Date(systemStatus.timestamp).toLocaleTimeString()}
                </div>
            </div>

            {/* Services Status */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Database */}
                <div className={`bg-finance-panel border ${services.database?.healthy ? 'border-electric-green/30' : 'border-red-500/30'} p-4 rounded-xl`}>
                    <div className="flex items-center gap-3 mb-2">
                        <Database size={20} className={services.database?.healthy ? 'text-electric-green' : 'text-red-500'} />
                        <span className="text-sm font-medium text-white">Database</span>
                    </div>
                    <div className="flex items-center gap-2">
                        {services.database?.healthy ? (
                            <>
                                <CheckCircle2 size={16} className="text-electric-green" />
                                <span className="text-xs text-electric-green">Online</span>
                            </>
                        ) : (
                            <>
                                <AlertCircle size={16} className="text-red-500" />
                                <span className="text-xs text-red-500">Offline</span>
                            </>
                        )}
                    </div>
                </div>

                {/* Email Service */}
                <div className={`bg-finance-panel border ${services.email?.enabled && services.email?.configured ? 'border-electric-green/30' : 'border-gray-700'} p-4 rounded-xl`}>
                    <div className="flex items-center gap-3 mb-2">
                        <Mail size={20} className={services.email?.enabled && services.email?.configured ? 'text-electric-green' : 'text-gray-500'} />
                        <span className="text-sm font-medium text-white">Email</span>
                    </div>
                    <div className="flex items-center gap-2">
                        {services.email?.enabled && services.email?.configured ? (
                            <>
                                <CheckCircle2 size={16} className="text-electric-green" />
                                <span className="text-xs text-electric-green">
                                    {services.email?.imap_listener ? 'Listening' : 'Configured'}
                                </span>
                            </>
                        ) : (
                            <>
                                <AlertCircle size={16} className="text-gray-500" />
                                <span className="text-xs text-gray-500">Disabled</span>
                            </>
                        )}
                    </div>
                </div>

                {/* AI Service */}
                <div className={`bg-finance-panel border ${services.ai?.enabled ? 'border-neon-purple/30' : 'border-gray-700'} p-4 rounded-xl`}>
                    <div className="flex items-center gap-3 mb-2">
                        <Cpu size={20} className={services.ai?.enabled ? 'text-neon-purple' : 'text-gray-500'} />
                        <span className="text-sm font-medium text-white">AI Service</span>
                    </div>
                    <div className="flex items-center gap-2">
                        {services.ai?.enabled ? (
                            <>
                                <CheckCircle2 size={16} className="text-neon-purple" />
                                <span className="text-xs text-neon-purple">Online</span>
                            </>
                        ) : (
                            <>
                                <AlertCircle size={16} className="text-gray-500" />
                                <span className="text-xs text-gray-500">Offline</span>
                            </>
                        )}
                    </div>
                    {services.ai?.model && (
                        <div className="mt-2 text-xs text-gray-500 truncate">
                            {services.ai.model}
                        </div>
                    )}
                </div>
            </div>

            {/* AI Token Usage */}
            {services.ai?.enabled && (
                <div className="bg-finance-panel border border-neon-purple/20 p-4 rounded-xl">
                    <div className="flex items-center gap-3 mb-3">
                        <Activity size={18} className="text-neon-purple" />
                        <span className="text-sm font-medium text-white">AI Token Usage</span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <div className="text-xs text-gray-500">Today Requests</div>
                            <div className="text-xl font-mono text-neon-purple">{aiUsage.today_requests || 0}</div>
                        </div>
                        <div>
                            <div className="text-xs text-gray-500">Today Tokens</div>
                            <div className="text-xl font-mono text-neon-purple">{(aiUsage.today_tokens || 0).toLocaleString()}</div>
                        </div>
                        <div>
                            <div className="text-xs text-gray-500">Total Requests</div>
                            <div className="text-xl font-mono text-white">{aiUsage.total_requests || 0}</div>
                        </div>
                        <div>
                            <div className="text-xs text-gray-500">Total Tokens</div>
                            <div className="text-xl font-mono text-white">{(aiUsage.total_tokens || 0).toLocaleString()}</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Transaction Sources (24h) */}
            <div className="bg-finance-panel border border-grid-border p-4 rounded-xl">
                <div className="mb-3">
                    <span className="text-sm font-medium text-white">Transaction Sources (24h)</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                        <div className="text-2xl font-mono text-white mb-1">{sources.total || 0}</div>
                        <div className="text-xs text-gray-500">Total</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-mono text-neon-purple mb-1">{sources.mobile || 0}</div>
                        <div className="text-xs text-gray-500">Mobile</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-mono text-blue-400 mb-1">{sources.email || 0}</div>
                        <div className="text-xs text-gray-500">Email</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-mono text-gray-400 mb-1">{sources.manual || 0}</div>
                        <div className="text-xs text-gray-500">Manual</div>
                    </div>
                </div>

                {/* Visual Flow Indicator */}
                <div className="mt-4 flex items-center justify-center gap-2">
                    <div className="flex flex-col items-center">
                        <div className="w-12 h-12 rounded-full bg-neon-purple/20 border border-neon-purple flex items-center justify-center">
                            <span className="text-xs font-bold text-neon-purple">📱</span>
                        </div>
                        <span className="text-xs text-gray-500 mt-1">Mobile</span>
                    </div>
                    <div className="text-gray-600">→</div>
                    <div className="flex flex-col items-center">
                        <div className="w-12 h-12 rounded-full bg-blue-500/20 border border-blue-500 flex items-center justify-center">
                            <span className="text-xs font-bold text-blue-400">📧</span>
                        </div>
                        <span className="text-xs text-gray-500 mt-1">Email</span>
                    </div>
                    <div className="text-gray-600">→</div>
                    <div className="flex flex-col items-center">
                        <div className="w-12 h-12 rounded-full bg-electric-green/20 border border-electric-green flex items-center justify-center">
                            <span className="text-xs font-bold text-electric-green">⚙️</span>
                        </div>
                        <span className="text-xs text-gray-500 mt-1">Processing</span>
                    </div>
                    <div className="text-gray-600">→</div>
                    <div className="flex flex-col items-center">
                        <div className="w-12 h-12 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center">
                            <span className="text-xs font-bold text-white">✓</span>
                        </div>
                        <span className="text-xs text-gray-500 mt-1">Complete</span>
                    </div>
                </div>
            </div>

            {/* Processing Queue */}
            <div className="bg-finance-panel border border-yellow-500/30 p-4 rounded-xl">
                <div className="mb-3">
                    <span className="text-sm font-medium text-white">Processing Queue</span>
                </div>
                <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                        <div className="text-3xl font-mono text-yellow-400 mb-1">{queue.pending || 0}</div>
                        <div className="text-xs text-gray-500">Pending</div>
                    </div>
                    <div className="text-center">
                        <div className="text-3xl font-mono text-orange-400 mb-1">{queue.draft || 0}</div>
                        <div className="text-xs text-gray-500">Draft</div>
                    </div>
                    <div className="text-center">
                        <div className="text-3xl font-mono text-white mb-1">{queue.total_waiting || 0}</div>
                        <div className="text-xs text-gray-500">Total</div>
                    </div>
                </div>
            </div>
        </div>
    );
};
