import React, { useState, useEffect } from 'react';
import { BentoBox } from '../components/ui/BentoBox';
import { Check, DollarSign, Tag, Link as LinkIcon, AlertTriangle, Sparkles, RefreshCw, Trash2, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { useStore, type Transaction, type Subscription } from '../context/StoreContext';
import { api } from '../services/api';

export const TransactionReview: React.FC = () => {
    const { subscriptions, actions } = useStore(); // Removed transactions from useStore
    const [transactions, setTransactions] = useState<Transaction[]>([]); // New state for API data
    const [loading, setLoading] = useState(true);
    // const [selectedTx] = useState<Transaction | null>(null); // Not used in this component

    const queue = transactions.filter(t => t.status === 'draft' || t.status === 'Pending');

    const [currentIndex, setCurrentIndex] = useState(0);
    const currentItem = queue[currentIndex];

    // Logic: Smart Matching
    const [matchedSubscription, setMatchedSubscription] = useState<Subscription | null>(null);
    const [matchType, setMatchType] = useState<'perfect' | 'mismatch' | 'potential' | 'none'>('none');
    const [variance, setVariance] = useState(0);

    // Fetch transactions from API
    useEffect(() => {
        const fetchTransactions = async () => {
            try {
                const data = await api.getTransactions(0, 100); // Get all transactions
                // Convert all IDs to strings
                const safeData = (data || []).map((tx: any) => ({
                    ...tx,
                    id: String(tx.id)
                }));
                setTransactions(safeData);
            } catch (error) {
                console.error('Failed to fetch transactions:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchTransactions();
    }, []);

    // Form State
    const [formData, setFormData] = useState<Partial<Transaction>>({});

    // Reset form when item changes
    useEffect(() => {
        if (currentItem) {
            setFormData({
                ...currentItem,
                isAmortized: false,
                amortizationMonths: 1,
                type: currentItem.type || 'expense'
            });

            // (Removed unused splitMode logic for now as it was causing lint errors and not used in this view iteration)

            // --- SMART MATCH LOGIC ---
            // 1. Try to find existing subscription
            const foundSub = subscriptions.find(s => currentItem.merchant.toLowerCase().includes(s.merchantKeyword));

            if (foundSub) {
                setMatchedSubscription(foundSub);
                const diff = currentItem.amount - foundSub.cost;
                setVariance(diff);

                if (Math.abs(diff) < 0.05) {
                    setMatchType('perfect');
                } else {
                    setMatchType('mismatch');
                }
            } else {
                // 2. Check for Potential New Subscription (Mock logic: Amount > 10 and recurring-sounding names)
                if (['adobe', 'hbomax', 'spotify'].some(k => currentItem.merchant.toLowerCase().includes(k))) {
                    setMatchType('potential');
                    setMatchedSubscription(null);
                } else {
                    setMatchType('none');
                    setMatchedSubscription(null);
                }
            }
        }
    }, [currentItem, subscriptions]);

    const handleApprove = async () => {
        if (!currentItem) return;

        try {
            // If it's a subscription match, update the Last Paid Date
            if (matchedSubscription) {
                actions.updateSubscription(matchedSubscription.id, {
                    lastPaidDate: currentItem.date,
                });
            }

            // Approve the transaction via API
            await api.approveTransaction(Number(currentItem.id));

            // Refresh transactions list
            const data = await api.getTransactions(0, 100);
            const safeData = (data || []).map((tx: any) => ({
                ...tx,
                id: String(tx.id)
            }));
            setTransactions(safeData);

            // Move to next item
            if (currentIndex < queue.length - 1) {
                setCurrentIndex(prev => prev + 1);
            } else {
                setCurrentIndex(0);
            }
        } catch (error) {
            console.error('Failed to approve transaction:', error);
            alert('Failed to approve transaction. Please try again.');
        }
    };

    const handleUpdateCostAndApprove = () => {
        if (!currentItem || !matchedSubscription) return;
        // Update global subscription cost
        actions.updateSubscription(matchedSubscription.id, { cost: currentItem.amount });
        // Then approve
        handleApprove();
    };

    const handleCreateSubscription = () => {
        // TODO: In production, this should open a subscription form modal
        handleApprove();
    };

    const handleReject = async () => {
        if (!currentItem) return;

        try {
            await api.deleteTransaction(Number(currentItem.id));

            // Refresh transactions list
            const data = await api.getTransactions(0, 100);
            const safeData = (data || []).map((tx: any) => ({
                ...tx,
                id: String(tx.id)
            }));
            setTransactions(safeData);

            // Move to next item
            if (currentIndex < queue.length - 1) {
                setCurrentIndex(prev => prev + 1);
            } else {
                setCurrentIndex(0);
            }
        } catch (error) {
            console.error('Failed to delete transaction:', error);
            alert('Failed to delete transaction. Please try again.');
        }
    };

    const handleSkip = () => {
        if (currentIndex < queue.length - 1) {
            setCurrentIndex(prev => prev + 1);
        } else {
            setCurrentIndex(0); // Loop back
        }
    };

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center text-gray-400">
                <div className="text-center">
                    <Loader2 size={48} className="mx-auto mb-4 text-neon-purple animate-spin" />
                    <h2 className="text-xl font-bold text-white">Loading Transactions...</h2>
                    <p>Fetching from database</p>
                </div>
            </div>
        );
    }

    if (!currentItem) {
        return (
            <div className="h-full flex items-center justify-center text-gray-400">
                <div className="text-center">
                    <Check size={48} className="mx-auto mb-4 text-electric-green" />
                    <h2 className="text-xl font-bold text-white">All Caught Up!</h2>
                    <p>Inboxes zeroed. Great job.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="h-full p-6 grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left: Source Document (Mock) */}
            <div className="flex flex-col gap-6">
                <BentoBox title="Original Source (Bank Feed)" className="h-full">
                    <div className="bg-white/5 rounded-xl p-6 h-[400px] font-mono text-sm relative border border-white/10 flex flex-col items-center justify-center">
                        <div className="text-center space-y-2">
                            <div className="w-16 h-16 bg-white/10 rounded-full mx-auto flex items-center justify-center mb-4">
                                <DollarSign className="text-gray-400" size={32} />
                            </div>
                            <div className="text-xl font-bold text-white">{currentItem.merchant}</div>
                            <div className="text-gray-400">{currentItem.date}</div>
                            <div className="text-4xl text-white py-4">${currentItem.amount.toFixed(2)}</div>
                            <div className="text-xs bg-black/40 px-3 py-1 rounded-full text-gray-500 inline-block">
                                ID: {currentItem.id.slice(0, 8)}
                            </div>
                        </div>
                    </div>
                </BentoBox>
            </div>

            {/* Right: Workbench */}
            <div className="flex flex-col gap-6">
                <div className="flex justify-between items-center text-gray-400 text-sm">
                    <span>Transaction {currentIndex + 1} of {queue.length}</span>
                    <span>Draft Mode</span>
                </div>

                {/* --- SMART MATCH CARDS --- */}
                {matchType === 'perfect' && matchedSubscription && (
                    <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="bg-gradient-to-r from-blue-900/40 to-black border border-blue-500/30 p-4 rounded-xl relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10"><LinkIcon size={100} /></div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="bg-blue-500 text-white p-1 rounded"><LinkIcon size={16} /></div>
                            <h3 className="text-blue-400 font-bold uppercase tracking-wider text-xs">Smart Match Detected</h3>
                        </div>
                        <p className="text-white text-lg font-medium mb-1">
                            Matches <span className="text-blue-200">{matchedSubscription.name}</span> subscription.
                        </p>
                        <p className="text-gray-400 text-sm">
                            Expected: <span className="font-mono text-white">${matchedSubscription.cost}</span> • Actual: <span className="font-mono text-white">${currentItem.amount}</span>
                        </p>
                    </motion.div>
                )}

                {matchType === 'mismatch' && matchedSubscription && (
                    <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="bg-gradient-to-r from-signal-orange/20 to-black border border-signal-orange/50 p-4 rounded-xl relative overflow-hidden">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="bg-signal-orange text-black p-1 rounded"><AlertTriangle size={16} /></div>
                            <h3 className="text-signal-orange font-bold uppercase tracking-wider text-xs">Price Mismatch Warning</h3>
                        </div>
                        <p className="text-white font-medium mb-1">
                            Subscription cost variance detected.
                        </p>
                        <div className="flex items-baseline gap-4 text-sm mt-2 p-3 bg-black/40 rounded-lg">
                            <div>
                                <span className="text-gray-500 block text-xs">Expected</span>
                                <span className="text-gray-300 font-mono line-through">${matchedSubscription.cost.toFixed(2)}</span>
                            </div>
                            <div className="text-gray-600">→</div>
                            <div>
                                <span className="text-gray-500 block text-xs">New Price</span>
                                <span className="text-white font-mono font-bold">${currentItem.amount.toFixed(2)}</span>
                            </div>
                            <div className="ml-auto text-signal-orange font-mono">
                                +{variance.toFixed(2)}
                            </div>
                        </div>
                    </motion.div>
                )}

                {matchType === 'potential' && (
                    <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="bg-gradient-to-r from-neon-purple/20 to-black border border-neon-purple/50 p-4 rounded-xl relative overflow-hidden">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="bg-neon-purple text-white p-1 rounded"><Sparkles size={16} /></div>
                            <h3 className="text-neon-purple font-bold uppercase tracking-wider text-xs">New Subscription?</h3>
                        </div>
                        <p className="text-white font-medium mb-1">
                            Looks like a recurring payment to <span className="text-white">{currentItem.merchant.split(' ')[0]}</span>.
                        </p>
                        <p className="text-gray-400 text-sm">
                            Would you like to track this as a fixed monthly expense?
                        </p>
                    </motion.div>
                )}


                {/* Main Workbench Form */}
                <BentoBox title="Review & Categorize">
                    <div className="px-6 py-4 space-y-6">
                        {/* Category */}
                        <div>
                            <label className="text-xs text-gray-500 font-bold uppercase tracking-wider mb-2 block">Category</label>
                            <div className="flex gap-2">
                                <div className="bg-white/5 border border-white/10 rounded-lg p-3 flex-1 flex justify-between items-center text-white">
                                    <span>{formData.category}</span>
                                    <Tag size={16} className="text-gray-500" />
                                </div>
                            </div>
                        </div>

                        {/* ACTIONS BAR */}
                        <div className="pt-4 border-t border-white/10">
                            {/* Scenario A: Perfect Match */}
                            {matchType === 'perfect' && (
                                <div className="flex gap-4">
                                    <button onClick={handleSkip} className="px-6 py-4 rounded-xl text-gray-400 hover:bg-white/5 transition-colors">Skip</button>
                                    <button
                                        onClick={handleApprove}
                                        className="flex-1 bg-blue-600 hover:bg-blue-500 text-white rounded-xl py-4 font-bold tracking-wide shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2"
                                    >
                                        <LinkIcon size={20} />
                                        Confirm Subscription
                                    </button>
                                </div>
                            )}

                            {/* Scenario B: Mismatch */}
                            {matchType === 'mismatch' && (
                                <div className="grid grid-cols-2 gap-4">
                                    <button
                                        onClick={handleUpdateCostAndApprove}
                                        className="col-span-2 bg-signal-orange hover:bg-orange-600 text-black font-bold rounded-xl py-4 flex items-center justify-center gap-2"
                                    >
                                        <RefreshCw size={20} />
                                        Update Cost to ${currentItem.amount}
                                    </button>
                                    <button onClick={handleApprove} className="bg-white/5 text-gray-300 hover:text-white rounded-xl py-3 text-sm font-medium">
                                        One-time Spike
                                    </button>
                                    <button onClick={handleSkip} className="bg-white/5 text-gray-500 hover:text-white rounded-xl py-3 text-sm font-medium">
                                        Skip Logic
                                    </button>
                                </div>
                            )}

                            {/* Scenario C: Potential */}
                            {matchType === 'potential' && (
                                <div className="flex gap-4">
                                    <button onClick={handleReject} className="p-4 rounded-xl text-gray-500 hover:bg-muted-red/10 hover:text-muted-red transition-colors"><Trash2 size={20} /></button>
                                    <button
                                        onClick={handleCreateSubscription}
                                        className="flex-1 bg-neon-purple hover:bg-purple-500 text-white rounded-xl py-4 font-bold tracking-wide shadow-lg shadow-purple-600/20 flex items-center justify-center gap-2"
                                    >
                                        <Sparkles size={20} />
                                        Create Subscription Entry
                                    </button>
                                </div>
                            )}

                            {/* Default / None */}
                            {matchType === 'none' && (
                                <div className="flex items-center gap-4">
                                    <button onClick={handleReject} className="p-4 rounded-xl text-gray-500 hover:bg-muted-red/10 hover:text-muted-red transition-colors" title="Reject / Delete">
                                        <Trash2 size={20} />
                                    </button>
                                    <button onClick={handleSkip} className="px-6 py-4 rounded-xl text-gray-400 hover:bg-white/5 hover:text-white transition-colors">
                                        Skip
                                    </button>
                                    <button
                                        onClick={handleApprove}
                                        className="flex-1 bg-gradient-to-r from-neon-purple to-indigo-600 rounded-xl py-4 text-white font-bold tracking-wide shadow-lg shadow-neon-purple/20 hover:shadow-neon-purple/40 active:scale-[0.98] transition-all flex items-center justify-center gap-2"
                                    >
                                        <Check size={20} />
                                        <span>Approve & Post</span>
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </BentoBox>
            </div>
        </div>
    );
};
