import React, { useState, useEffect } from 'react';
import { BentoBox } from '../components/ui/BentoBox';
import { TrendingUp, Home, Car, DollarSign, Loader2, AlertTriangle, X, Plus, CheckCircle2, Clock } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';
import { useStore, type Asset, type Subscription } from '../context/StoreContext';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../services/api';

export const AssetHub: React.FC = () => {
    const { transactions, subscriptions, actions } = useStore(); // Removed assets from useStore
    const [assets, setAssets] = useState<any[]>([]); // New state for assets fetched from API
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);

    // Fetch assets from API
    useEffect(() => {
        const fetchAssets = async () => {
            try {
                const data = await api.getAssets();
                setAssets(data);
            } catch (error) {
                console.error('Failed to fetch assets:', error);
                setError('Failed to load assets');
            } finally {
                setLoading(false);
            }
        };
        fetchAssets();
    }, []);

    // Modal States
    const [isAddAssetOpen, setIsAddAssetOpen] = useState(false);
    const [isDividendOpen, setIsDividendOpen] = useState(false);

    // Edit Mode States
    const [isEditMode, setIsEditMode] = useState(false);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [editForm, setEditForm] = useState({
        name: '',
        type: '',
        value: 0,
        equity: 0
    });

    // New Asset Form
    const [newAsset, setNewAsset] = useState<Partial<Asset>>({ type: 'Stock', value: 0, equity: 0 });

    // Dividend Form
    const [dividendAmount, setDividendAmount] = useState('');

    const getAssetIcon = (type: string) => {
        switch (type) {
            case 'Vehicle': return <Car size={24} />;
            case 'RealEstate': return <Home size={24} />;
            default: return <TrendingUp size={24} />;
        }
    };

    const getSubscriptionStatus = (sub: Subscription) => {
        // Mock logic for status based on ID for demo purposes
        if (sub.merchantKeyword === 'rogers') return <span className="flex items-center gap-1 text-signal-orange text-xs bg-signal-orange/10 px-2 py-0.5 rounded"><AlertTriangle size={12} /> Price Alert</span>;
        if (sub.merchantKeyword === 'prime') return <span className="flex items-center gap-1 text-blue-400 text-xs bg-blue-400/10 px-2 py-0.5 rounded"><Clock size={12} /> Pending Renewal</span>;
        return <span className="flex items-center gap-1 text-electric-green text-xs bg-electric-green/10 px-2 py-0.5 rounded"><CheckCircle2 size={12} /> Active</span>;
    };

    const getNextDue = (sub: Subscription) => {
        // Hardcoded for demo/mock match
        if (sub.merchantKeyword === 'netflix') return 'Nov 15';
        if (sub.merchantKeyword === 'rogers') return 'Nov 20';
        if (sub.merchantKeyword === 'prime') return 'Jan 05';
        return 'Unknown';
    };

    // Mock value history for chart
    const data = [
        { name: 'Jan', value: 40000 },
        { name: 'Feb', value: 40500 },
        { name: 'Mar', value: 42000 },
        { name: 'Apr', value: 41500 },
        { name: 'May', value: 45000 },
    ];

    const handleCreateAsset = async () => {
        if (!newAsset.name || !newAsset.value) return;

        try {
            await api.addAsset({
                name: newAsset.name,
                type: newAsset.type,
                value: Number(newAsset.value),
                equity: Number(newAsset.equity || newAsset.value)
            });

            // Refresh assets list
            const data = await api.getAssets();
            setAssets(data);

            setIsAddAssetOpen(false);
            setNewAsset({ type: 'Stock', value: 0, equity: 0, name: '' });
        } catch (error) {
            console.error('Failed to create asset:', error);
            alert('Failed to create asset. Please try again.');
        }
    };

    const handleUpdateAsset = async () => {
        if (!selectedAsset || !editForm.name || !editForm.value) return;

        try {
            await api.updateAsset(Number(selectedAsset.id), {
                name: editForm.name,
                type: editForm.type,
                value: Number(editForm.value),
                equity: Number(editForm.equity || editForm.value)
            });

            // Refresh assets list
            const data = await api.getAssets();
            setAssets(data);

            // Update selected asset with new data
            const updatedAsset = data.find((a: any) => a.id === selectedAsset.id);
            if (updatedAsset) {
                setSelectedAsset(updatedAsset);
            }

            setIsEditMode(false);
            setShowDeleteConfirm(false);
        } catch (error) {
            console.error('Failed to update asset:', error);
            alert('Failed to update asset. Please try again.');
        }
    };

    const handleDeleteAsset = async () => {
        if (!selectedAsset) return;

        try {
            await api.deleteAsset(Number(selectedAsset.id));

            // Refresh assets list
            const data = await api.getAssets();
            setAssets(data);

            // Close the panel
            setSelectedAsset(null);
            setIsEditMode(false);
            setShowDeleteConfirm(false);
        } catch (error) {
            console.error('Failed to delete asset:', error);
            alert('Failed to delete asset. Please try again.');
        }
    };

    const handleRecordDividend = () => {
        if (!selectedAsset || !dividendAmount) return;
        actions.addTransaction({
            merchant: `${selectedAsset.name} Dividend`,
            amount: parseFloat(dividendAmount),
            category: 'Investment Income',
            type: 'income',
            date: new Date().toISOString().split('T')[0],
            assetId: selectedAsset.id
        });
        setIsDividendOpen(false);
        setDividendAmount('');
    };

    // const totalValue = assets.reduce((sum, a) => sum + (a.current_value || 0), 0);
    // const totalGain = assets.reduce((sum, a) => {
    //     const gain = (a.current_value || 0) - (a.purchase_price || 0);
    //     return sum + gain;
    // }, 0);

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="text-center">
                    <Loader2 size={48} className="mx-auto mb-4 text-neon-purple animate-spin" />
                    <h2 className="text-xl font-bold text-white">Loading Assets...</h2>
                    <p className="text-gray-400">Fetching from database</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="text-center">
                    <AlertTriangle size={48} className="mx-auto mb-4 text-signal-orange" />
                    <h2 className="text-xl font-bold text-white">Error Loading Assets</h2>
                    <p className="text-gray-400">{error}</p>
                </div>
            </div>
        );
    }

    const assetHistory = selectedAsset ? transactions.filter(t => t.assetId === selectedAsset.id || (t.merchant.includes(selectedAsset.name))) : [];

    // ... (Keep existing Modal/Slideover code exactly as is, it's good) ...
    // Re-pasting entire file for replace_file_content tool safety to avoid partial match errors

    return (
        <div className="h-full p-6 relative overflow-y-auto">
            {/* Asset Details Modal / Slide-over */}
            <AnimatePresence>
                {selectedAsset && (
                    <motion.div
                        initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
                        className="absolute top-0 right-0 bottom-0 w-full md:w-[450px] bg-black/90 backdrop-blur-xl border-l border-grid-border z-40 p-6 flex flex-col shadow-2xl"
                    >
                        <div className="flex justify-between items-center mb-8">
                            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                {getAssetIcon(selectedAsset.type)}
                                {isEditMode ? 'Edit Asset' : selectedAsset.name}
                            </h2>
                            <button onClick={() => { setSelectedAsset(null); setIsEditMode(false); }} className="p-2 hover:bg-white/10 rounded-full text-gray-400 hover:text-white">
                                <X size={20} />
                            </button>
                        </div>

                        {/* Edit Mode Form */}
                        {isEditMode ? (
                            <div className="space-y-4 flex-1">
                                <div>
                                    <label className="text-xs text-gray-400 block mb-1">Asset Name</label>
                                    <input
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none"
                                        value={editForm.name}
                                        onChange={e => setEditForm({ ...editForm, name: e.target.value })}
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-xs text-gray-400 block mb-1">Type</label>
                                        <select
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none"
                                            value={editForm.type}
                                            onChange={e => setEditForm({ ...editForm, type: e.target.value })}
                                        >
                                            <option value="Equity">Equity / Stock</option>
                                            <option value="RealEstate">Real Estate</option>
                                            <option value="Vehicle">Vehicle</option>
                                            <option value="Business">Business Interest</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="text-xs text-gray-400 block mb-1">Current Value</label>
                                        <input
                                            type="number"
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none font-mono"
                                            value={editForm.value}
                                            onChange={e => setEditForm({ ...editForm, value: Number(e.target.value) })}
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="text-xs text-gray-400 block mb-1">Equity Owned</label>
                                    <input
                                        type="number"
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none font-mono"
                                        value={editForm.equity}
                                        onChange={e => setEditForm({ ...editForm, equity: Number(e.target.value) })}
                                    />
                                </div>

                                <div className="flex gap-3 mt-6">
                                    <button
                                        onClick={handleUpdateAsset}
                                        className="flex-1 bg-neon-purple hover:bg-neon-purple/80 text-white font-bold py-3 rounded-xl transition-colors"
                                    >
                                        Save Changes
                                    </button>
                                    <button
                                        onClick={() => setIsEditMode(false)}
                                        className="flex-1 bg-white/5 hover:bg-white/10 text-gray-300 font-bold py-3 rounded-xl transition-colors"
                                    >
                                        Cancel
                                    </button>
                                </div>

                                {/* Delete Button */}
                                <div className="mt-4 pt-4 border-t border-grid-border">
                                    {showDeleteConfirm ? (
                                        <div className="bg-red-500/10 border border-red-500/30 p-4 rounded-xl">
                                            <p className="text-red-400 text-sm mb-3">Are you sure you want to delete this asset? This action cannot be undone.</p>
                                            <div className="flex gap-2">
                                                <button
                                                    onClick={handleDeleteAsset}
                                                    className="flex-1 bg-red-500 hover:bg-red-600 text-white font-bold py-2 rounded-lg transition-colors"
                                                >
                                                    Yes, Delete
                                                </button>
                                                <button
                                                    onClick={() => setShowDeleteConfirm(false)}
                                                    className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-bold py-2 rounded-lg transition-colors"
                                                >
                                                    Cancel
                                                </button>
                                            </div>
                                        </div>
                                    ) : (
                                        <button
                                            onClick={() => setShowDeleteConfirm(true)}
                                            className="w-full bg-red-500/10 text-red-400 hover:bg-red-500/20 py-2 rounded-lg text-sm font-medium transition-colors"
                                        >
                                            Delete Asset
                                        </button>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <>
                                <div className="mb-6 p-4 bg-white/5 rounded-xl border border-white/10">
                                    <div className="flex justify-between items-end mb-2">
                                        <div className="text-sm text-gray-500">Current Valuation</div>
                                        <div className="text-xs text-electric-green bg-electric-green/10 px-2 py-0.5 rounded">Live</div>
                                    </div>
                                    <div className="text-3xl font-mono text-white mb-1">${selectedAsset.value.toLocaleString()}</div>
                                    {selectedAsset.equity && (
                                        <div className="text-sm text-gray-400 flex justify-between">
                                            <span>Equity Owned</span>
                                            <span className="text-white">${selectedAsset.equity.toLocaleString()}</span>
                                        </div>
                                    )}
                                </div>

                                <div className="grid grid-cols-2 gap-3 mb-6">
                                    <button
                                        onClick={() => setIsDividendOpen(true)}
                                        className="bg-electric-green/10 text-electric-green hover:bg-electric-green hover:text-black py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
                                    >
                                        <DollarSign size={16} />
                                        Record Income
                                    </button>
                                    <button
                                        onClick={() => {
                                            setEditForm({
                                                name: selectedAsset.name,
                                                type: selectedAsset.type,
                                                value: selectedAsset.value,
                                                equity: selectedAsset.equity || selectedAsset.value
                                            });
                                            setIsEditMode(true);
                                        }}
                                        className="bg-neon-purple/10 text-neon-purple hover:bg-neon-purple hover:text-white py-2 rounded-lg text-sm font-medium transition-colors"
                                    >
                                        Edit Details
                                    </button>
                                </div>

                                <AnimatePresence>
                                    {isDividendOpen && (
                                        <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden mb-6">
                                            <div className="bg-neon-purple/10 border border-neon-purple/30 p-4 rounded-xl">
                                                <h4 className="text-white text-sm font-medium mb-3">Record New Income</h4>
                                                <div className="flex gap-2">
                                                    <input
                                                        type="number"
                                                        placeholder="0.00"
                                                        className="flex-1 bg-black/40 border border-grid-border rounded px-3 py-2 text-white outline-none focus:border-neon-purple"
                                                        value={dividendAmount}
                                                        onChange={e => setDividendAmount(e.target.value)}
                                                        autoFocus
                                                    />
                                                    <button onClick={handleRecordDividend} className="bg-neon-purple text-white px-4 rounded font-bold hover:bg-neon-purple/80">
                                                        Save
                                                    </button>
                                                </div>
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>

                                <div className="flex-1 overflow-y-auto">
                                    <h3 className="text-xs uppercase tracking-wider text-gray-500 mb-4 font-semibold">Activity Log</h3>
                                    <div className="space-y-4">
                                        {assetHistory.length === 0 ? (
                                            <p className="text-gray-600 text-sm text-center py-4">No recorded history.</p>
                                        ) : (
                                            <div className="relative pl-4 border-l border-white/10 space-y-6">
                                                {assetHistory.map((tx) => (
                                                    <div key={tx.id} className="relative">
                                                        <div className={`absolute -left-[21px] top-1 w-3 h-3 rounded-full border-2 border-black ${tx.type === 'income' ? 'bg-electric-green' : 'bg-grid-border'} `} />
                                                        <div className="text-sm text-gray-300">{tx.category}</div>
                                                        <div className="text-xs text-gray-500 mb-1">{tx.date} • {tx.merchant}</div>
                                                        <div className={`font-mono text-sm ${tx.type === 'income' ? 'text-electric-green' : 'text-white'} `}>
                                                            {tx.type === 'income' ? '+' : '-'}${tx.amount.toLocaleString()}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Add Asset Modal */}
            <AnimatePresence>
                {isAddAssetOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setIsAddAssetOpen(false)} />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-finance-panel border border-grid-border rounded-2xl p-6 w-full max-w-md relative z-10 shadow-2xl"
                        >
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-xl font-bold text-white">Add New Asset</h3>
                                <button onClick={() => setIsAddAssetOpen(false)} className="text-gray-400 hover:text-white"><X size={20} /></button>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <label className="text-xs text-gray-400 block mb-1">Asset Name</label>
                                    <input
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none"
                                        value={newAsset.name || ''}
                                        onChange={e => setNewAsset({ ...newAsset, name: e.target.value })}
                                        placeholder="e.g. Nvidia Stock, Rental Property"
                                        autoFocus
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-xs text-gray-400 block mb-1">Type</label>
                                        <select
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none"
                                            value={newAsset.type}
                                            onChange={e => setNewAsset({ ...newAsset, type: e.target.value as any })}
                                        >
                                            <option value="Equity">Equity / Stock</option>
                                            <option value="RealEstate">Real Estate</option>
                                            <option value="Vehicle">Vehicle</option>
                                            <option value="Business">Business Interest</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="text-xs text-gray-400 block mb-1">Full Value</label>
                                        <input
                                            type="number"
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none font-mono"
                                            value={newAsset.value || ''}
                                            onChange={e => setNewAsset({ ...newAsset, value: Number(e.target.value) })}
                                            placeholder="0.00"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="text-xs text-gray-400 block mb-1">Equity Owned (Optional)</label>
                                    <input
                                        type="number"
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white focus:border-neon-purple outline-none font-mono"
                                        value={newAsset.equity || ''}
                                        onChange={e => setNewAsset({ ...newAsset, equity: Number(e.target.value) })}
                                        placeholder="Same as value if fully owned"
                                    />
                                    <p className="text-[10px] text-gray-500 mt-1">For mortgaged properties, enter your actual equity.</p>
                                </div>

                                <button
                                    onClick={handleCreateAsset}
                                    className="w-full bg-neon-purple hover:bg-neon-purple/80 text-white font-bold py-3 rounded-xl mt-4 transition-colors"
                                >
                                    Create Asset
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            <header className="mb-8 flex justify-between items-end">
                <h1 className="text-3xl font-light text-white mb-2">Asset & Subscription <span className="text-neon-purple">Hub</span></h1>
                <button
                    onClick={() => setIsAddAssetOpen(true)}
                    className="bg-white/5 hover:bg-white/10 text-white border border-grid-border px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors"
                >
                    <Plus size={18} />
                    <span>Add Asset</span>
                </button>
            </header>

            {/* Assets Grid */}
            <h2 className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-4">High-Value Assets</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {assets.map(asset => (
                    <BentoBox key={asset.id} className="cursor-pointer hover:border-neon-purple transition-colors group" onClick={() => setSelectedAsset(asset)}>
                        <div className="flex justify-between items-start mb-4">
                            <div className="w-10 h-10 rounded bg-white/5 flex items-center justify-center text-neon-purple group-hover:bg-neon-purple group-hover:text-white transition-colors">
                                {getAssetIcon(asset.type)}
                            </div>
                            {asset.type === 'Vehicle' && <div className="text-xs bg-red-500/10 text-red-500 px-2 py-1 rounded">Depreciating</div>}
                            {asset.type === 'RealEstate' && <div className="text-xs bg-green-500/10 text-green-500 px-2 py-1 rounded">Appreciating</div>}
                            {asset.type === 'Equity' && <div className="text-xs bg-blue-500/10 text-blue-500 px-2 py-1 rounded">Liquid</div>}
                        </div>
                        <div className="mt-2">
                            <h3 className="text-white font-medium truncate">{asset.name}</h3>
                            <div className="text-2xl font-mono py-2">${asset.value.toLocaleString()}</div>
                        </div>
                        <div className="h-16 -mx-6 -mb-6 mt-2 opacity-50 group-hover:opacity-100 transition-opacity">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={data}>
                                    <Area type="monotone" dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.1} strokeWidth={2} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </BentoBox>
                ))}
            </div>

            {/* Subscriptions - DYNAMIC */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <BentoBox title="Recurring Obligations (Expected Expenses)">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="text-xs text-gray-500 border-b border-grid-border">
                                    <th className="pb-3 font-medium">Service / Merchant</th>
                                    <th className="pb-3 font-medium">Cost</th>
                                    <th className="pb-3 font-medium">Cycle</th>
                                    <th className="pb-3 font-medium">Next Due</th>
                                    <th className="pb-3 font-medium text-right">Status</th>
                                </tr>
                            </thead>
                            <tbody className="text-sm">
                                {subscriptions.map((sub) => (
                                    <tr key={sub.id} className="border-b border-white/5 group hover:bg-white/5 transition-colors">
                                        <td className="py-3 text-white">
                                            {sub.name}
                                            <div className="text-[10px] text-gray-500">{sub.paymentMethod}</div>
                                        </td>
                                        <td className="py-3 font-mono text-white">${sub.cost.toFixed(2)}</td>
                                        <td className="py-3 text-gray-400">{sub.billingCycle}</td>
                                        <td className="py-3 text-gray-300">{getNextDue(sub)}</td>
                                        <td className="py-3 flex justify-end">
                                            {getSubscriptionStatus(sub)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </BentoBox>
                </div>
            </div>
        </div>
    );
};

