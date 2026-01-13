import React, { useState, useMemo, useEffect } from 'react';
import { BentoBox } from '../components/ui/BentoBox';
import { Shield, Lock, CreditCard, Plus, X, Heart, Home, Car, TrendingUp, AlertCircle, Calendar, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../services/api';

export const BenefitsLocker: React.FC = () => {
    // const { actions } = useStore(); // Removed - using API directly now
    const [accounts, setAccounts] = useState<any[]>([]);
    const [insurancePolicies, setInsurancePolicies] = useState<any[]>([]);
    const [govBenefits, setGovBenefits] = useState<any[]>([]);
    const [annualBenefitsTotal, setAnnualBenefitsTotal] = useState<number>(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string>('');

    // Fetch data from API
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [accountsData, policiesData, benefitsData, benefitsSummary] = await Promise.all([
                    api.getAccounts(),
                    api.getPolicies(),
                    api.getGovBenefits(true),
                    api.getAnnualBenefitsSummary()
                ]);
                setAccounts(accountsData || []);
                setInsurancePolicies(policiesData || []);
                setGovBenefits(benefitsData || []);
                setAnnualBenefitsTotal(benefitsSummary?.total_annual_benefits || 0);
                setError('');
            } catch (error: any) {
                console.error('Failed to fetch benefits data:', error);
                setError(error.response?.data?.detail || error.message || 'Failed to load benefits data');
                setAccounts([]);
                setGovBenefits([]);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // Modal States
    const [isInsuranceModalOpen, setIsInsuranceModalOpen] = useState(false);
    const [isAccountModalOpen, setIsAccountModalOpen] = useState(false);
    const [isGovBenefitModalOpen, setIsGovBenefitModalOpen] = useState(false);
    const [editingBenefit, setEditingBenefit] = useState<any>(null);

    // Forms
    const [newPolicy, setNewPolicy] = useState<any>({ type: 'Auto', frequency: 'Monthly' });
    const [newAccount, setNewAccount] = useState<any>({ type: 'TFSA' });
    const [newBenefit, setNewBenefit] = useState<any>({
        name: '',
        benefit_type: 'CCB',
        amount: 0,
        frequency: 'MONTHLY',
        government_agency: 'Government of Canada',
        is_active: true
    });

    // Map API accounts to registered accounts format (with safe checks)
    const registeredAccounts = (accounts || []).map(acc => ({
        id: String(acc.id),  // Convert ID to string
        type: acc.type || 'TFSA',
        institution: acc.institution || 'Questrade',
        holder: acc.holder || 'Family',
        currentValue: acc.current_value || 0,
        contributionRoom: acc.contribution_room
    }));

    // Mock insurance policies (not in current API)
    // const insurancePolicies: any[] = []; // REPLACED BY STATE

    // --- INSIGHTS CALCULATIONS ---
    const insights = useMemo(() => {
        let annualInsuranceCost = 0;
        insurancePolicies.forEach(p => {
            annualInsuranceCost += p.frequency === 'Monthly' ? p.premium * 12 : p.premium;
        });

        // Use real annual benefits from API
        const annualGovBenefits = annualBenefitsTotal;

        // Contribution Room
        let totalRoom = 0;
        let totalInvested = 0;
        registeredAccounts.forEach(a => {
            totalRoom += a.contributionRoom;
            totalInvested += a.currentValue;
        });

        // Nearest Renewal
        const today = new Date();
        const upcomingPolicies = [...insurancePolicies].sort((a, b) => new Date(a.renewalDate).getTime() - new Date(b.renewalDate).getTime());
        const nextRenewal = upcomingPolicies.find(p => new Date(p.renewalDate) > today) || upcomingPolicies[0];

        return {
            annualInsuranceCost,
            annualGovBenefits,
            coverageRatio: annualInsuranceCost > 0 ? (annualGovBenefits / annualInsuranceCost) * 100 : 0,
            totalRoom,
            totalInvested,
            nextRenewal
        };
    }, [insurancePolicies, registeredAccounts, annualBenefitsTotal]);

    // Progress Bar Helper
    const ProgressBar = ({ current, max, color = "bg-electric-green" }: { current: number, max?: number, color?: string }) => {
        const percentage = max ? Math.min(100, (current / max) * 100) : 0;
        return (
            <div className="w-full h-2 bg-gray-700 rounded-full mt-2 overflow-hidden">
                <div className={`h-full ${color} `} style={{ width: `${percentage}% ` }} />
            </div>
        );
    };

    const handleAddPolicy = async () => {
        if (!newPolicy.provider || !newPolicy.premium) return;

        try {
            await api.addPolicy({
                provider: newPolicy.provider,
                type: newPolicy.type,
                policy_number: newPolicy.policyNumber || 'N/A',
                renewal_date: newPolicy.renewalDate || new Date().toISOString().split('T')[0],
                premium: Number(newPolicy.premium),
                frequency: newPolicy.frequency,
                insured_item: newPolicy.insuredItem
            });

            // Refresh Data
            const policiesData = await api.getPolicies();
            setInsurancePolicies(policiesData || []);

            setIsInsuranceModalOpen(false);
            setNewPolicy({ type: 'Auto', frequency: 'Monthly', provider: '', insuredItem: '', policyNumber: '', premium: 0 });
        } catch (err) {
            console.error("Failed to add policy:", err);
            alert("Failed to add policy. Please check values.");
        }
    };

    const handleAddAccount = async () => {
        if (!newAccount.institution || !newAccount.currentValue) {
            alert("Please fill in required fields");
            return;
        }

        try {
            await api.addAccount({
                type: newAccount.type,
                institution: newAccount.institution,
                holder: newAccount.holder || 'Family',
                current_value: Number(newAccount.currentValue),
                contribution_room: Number(newAccount.contributionRoom || 0)
            });

            // Refresh accounts
            const accountsData = await api.getAccounts();
            setAccounts(accountsData || []);

            setIsAccountModalOpen(false);
            setNewAccount({ type: 'TFSA', institution: '', holder: '', currentValue: 0, contributionRoom: 0 });
        } catch (err) {
            console.error("Failed to add account:", err);
            alert("Failed to add account. Please check values.");
        }
    };

    const handleAddOrUpdateBenefit = async () => {
        if (!newBenefit.name || !newBenefit.amount) {
            alert("Please fill in required fields (Name and Amount)");
            return;
        }

        try {
            if (editingBenefit) {
                // Update existing benefit
                await api.updateGovBenefit(editingBenefit.id, {
                    name: newBenefit.name,
                    benefit_type: newBenefit.benefit_type,
                    amount: Number(newBenefit.amount),
                    frequency: newBenefit.frequency,
                    next_payment_date: newBenefit.next_payment_date || null,
                    government_agency: newBenefit.government_agency,
                    beneficiary: newBenefit.beneficiary || null,
                    notes: newBenefit.notes || null,
                    is_active: newBenefit.is_active
                });
            } else {
                // Create new benefit
                await api.createGovBenefit({
                    name: newBenefit.name,
                    benefit_type: newBenefit.benefit_type,
                    amount: Number(newBenefit.amount),
                    frequency: newBenefit.frequency,
                    next_payment_date: newBenefit.next_payment_date || null,
                    government_agency: newBenefit.government_agency,
                    beneficiary: newBenefit.beneficiary || null,
                    notes: newBenefit.notes || null,
                    is_active: newBenefit.is_active
                });
            }

            // Refresh benefits data
            const [benefitsData, benefitsSummary] = await Promise.all([
                api.getGovBenefits(true),
                api.getAnnualBenefitsSummary()
            ]);
            setGovBenefits(benefitsData || []);
            setAnnualBenefitsTotal(benefitsSummary?.total_annual_benefits || 0);

            // Close modal and reset form
            setIsGovBenefitModalOpen(false);
            setEditingBenefit(null);
            setNewBenefit({
                name: '',
                benefit_type: 'CCB',
                amount: 0,
                frequency: 'MONTHLY',
                government_agency: 'Government of Canada',
                is_active: true
            });
        } catch (err) {
            console.error("Failed to save benefit:", err);
            alert("Failed to save benefit. Please check values.");
        }
    };

    const handleEditBenefit = (benefit: any) => {
        setEditingBenefit(benefit);
        setNewBenefit({
            name: benefit.name,
            benefit_type: benefit.benefit_type,
            amount: benefit.amount,
            frequency: benefit.frequency,
            next_payment_date: benefit.next_payment_date || '',
            government_agency: benefit.government_agency || 'Government of Canada',
            beneficiary: benefit.beneficiary || '',
            notes: benefit.notes || '',
            is_active: benefit.is_active
        });
        setIsGovBenefitModalOpen(true);
    };

    const handleDeleteBenefit = async (id: number) => {
        if (!confirm("Are you sure you want to delete this benefit?")) return;

        try {
            await api.deleteGovBenefit(id);

            // Refresh benefits data
            const [benefitsData, benefitsSummary] = await Promise.all([
                api.getGovBenefits(true),
                api.getAnnualBenefitsSummary()
            ]);
            setGovBenefits(benefitsData || []);
            setAnnualBenefitsTotal(benefitsSummary?.total_annual_benefits || 0);
        } catch (err) {
            console.error("Failed to delete benefit:", err);
            alert("Failed to delete benefit.");
        }
    };

    if (loading) {
        return (
            <div className="p-6 h-full flex items-center justify-center">
                <div className="text-center">
                    <Loader2 size={48} className="mx-auto mb-4 text-neon-purple animate-spin" />
                    <h2 className="text-xl font-bold text-white">Loading Benefits...</h2>
                    <p className="text-gray-400">Fetching from database</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-6 h-full flex items-center justify-center">
                <div className="text-center">
                    <AlertCircle size={48} className="mx-auto mb-4 text-signal-orange" />
                    <h2 className="text-xl font-bold text-white">Error Loading Benefits</h2>
                    <p className="text-gray-400 mb-4">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="bg-neon-purple hover:bg-purple-600 text-white px-6 py-2 rounded-lg font-medium"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 h-full overflow-y-auto relative">
            <header className="mb-8 flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-light text-white mb-1 tracking-tight">Coverage & <span className="text-gray-500">Accounts</span></h1>
                    <p className="text-gray-500 text-sm">Insurance Portfolio • Registered Assets • Gov Benefits</p>
                </div>
            </header>

            {/* --- STRATEGY COCKPIT (INSIGHTS) --- */}
            <h2 className="text-gray-400 text-sm font-medium uppercase tracking-wider mb-4 flex items-center gap-2">
                <TrendingUp size={16} /> Strategy Cockpit
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                {/* Card 1: Tax Efficiency */}
                <div className="bg-gradient-to-br from-blue-900/40 to-black border border-blue-500/30 p-5 rounded-2xl relative overflow-hidden group hover:border-blue-500/60 transition-colors">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity"><Lock size={80} /></div>
                    <div className="flex items-center gap-2 mb-2 text-blue-400">
                        <Lock size={18} />
                        <span className="font-bold text-xs uppercase tracking-wider">Tax Free Room</span>
                    </div>
                    <div className="text-3xl font-mono text-white mb-1">${insights.totalRoom.toLocaleString()}</div>
                    <p className="text-xs text-gray-400 mb-4">Unused Contribution Space</p>
                    <div className="w-full bg-blue-900/30 h-1.5 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500" style={{ width: `${(insights.totalInvested / (insights.totalInvested + insights.totalRoom)) * 100}% ` }} />
                    </div>
                    <div className="text-[10px] text-gray-500 mt-2 flex justify-between">
                        <span>${((insights.totalInvested / 1000)).toFixed(1)}k Invested</span>
                        <span>Target: Maxed</span>
                    </div>
                </div>

                {/* Card 2: Protection vs Cost */}
                <div className="bg-gradient-to-br from-emerald-900/40 to-black border border-emerald-500/30 p-5 rounded-2xl relative overflow-hidden group hover:border-emerald-500/60 transition-colors">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity"><Shield size={80} /></div>
                    <div className="flex items-center gap-2 mb-2 text-emerald-400">
                        <Shield size={18} />
                        <span className="font-bold text-xs uppercase tracking-wider">Protection Cost</span>
                    </div>
                    <div className="flex items-baseline gap-2">
                        <div className="text-2xl font-mono text-white mb-1">${insights.annualInsuranceCost.toLocaleString()}</div>
                        <div className="text-xs text-gray-400">/yr</div>
                    </div>

                    <div className="mt-2 p-2 bg-black/40 rounded-lg flex items-center justify-between border border-white/5">
                        <span className="text-xs text-gray-400">Gov. Benefits</span>
                        <span className="text-xs text-electric-green font-mono">+${insights.annualGovBenefits.toLocaleString()}/yr</span>
                    </div>
                    <div className="text-[10px] text-gray-500 mt-2">
                        Benefits cover <span className="text-white font-bold">{insights.coverageRatio.toFixed(0)}%</span> of insurance costs.
                    </div>
                </div>

                {/* Card 3: Renewal Monitor */}
                <div className="bg-gradient-to-br from-amber-900/40 to-black border border-amber-500/30 p-5 rounded-2xl relative overflow-hidden group hover:border-amber-500/60 transition-colors">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity"><Calendar size={80} /></div>
                    <div className="flex items-center gap-2 mb-2 text-amber-400">
                        <AlertCircle size={18} />
                        <span className="font-bold text-xs uppercase tracking-wider">Renewal Watch</span>
                    </div>

                    {insights.nextRenewal ? (
                        <>
                            <div className="text-lg font-bold text-white mb-1 truncate">{insights.nextRenewal.provider}</div>
                            <div className="text-sm text-amber-200 mb-4">{insights.nextRenewal.type} Policy</div>
                            <div className="flex items-center gap-3 bg-amber-500/10 p-2 rounded-lg border border-amber-500/20">
                                <div className="text-center px-2 border-r border-amber-500/20">
                                    <div className="text-xs text-amber-500 font-bold uppercase">{new Date(insights.nextRenewal.renewalDate).toLocaleString('default', { month: 'short' })}</div>
                                    <div className="text-lg font-bold text-white">{new Date(insights.nextRenewal.renewalDate).getDate()}</div>
                                </div>
                                <div className="text-xs text-gray-300">
                                    Check for better rates before auto-renewal.
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="flex items-center h-20 text-gray-500 text-sm">No upcoming renewals.</div>
                    )}
                </div>
            </div>

            {/* SECTION 1: INSURANCE PORTFOLIO */}
            <div className="mb-8">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-gray-400 text-sm font-medium uppercase tracking-wider flex items-center gap-2">
                        <Shield size={16} /> Insurance Portfolio
                    </h2>
                    <button onClick={() => setIsInsuranceModalOpen(true)} className="text-xs bg-white/5 hover:bg-white/10 text-white px-3 py-1.5 rounded flex items-center gap-1">
                        <Plus size={14} /> Add Policy
                    </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {insurancePolicies.map(policy => (
                        <BentoBox key={policy.id} className="relative group">
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded bg-blue-500/10 flex items-center justify-center text-blue-400">
                                        {policy.type === 'Auto' && <Car size={20} />}
                                        {policy.type === 'Home' && <Home size={20} />}
                                        {policy.type === 'Life' && <Heart size={20} />}
                                    </div>
                                    <div>
                                        <div className="text-white font-medium">{policy.provider}</div>
                                        <div className="text-xs text-gray-500">{policy.type} Policy</div>
                                    </div>
                                </div>
                            </div>
                            <div className="space-y-2 text-sm text-gray-300">
                                {policy.insuredItem && <div className="text-xs text-gray-500">{policy.insuredItem}</div>}
                                <div className="flex justify-between">
                                    <span>Premium</span>
                                    <span className="font-mono text-white">${policy.premium}/{policy.frequency === 'Monthly' ? 'mo' : 'yr'}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span>Renewal</span>
                                    <span className="text-electric-green">{policy.renewalDate}</span>
                                </div>
                                <div className="text-xs text-gray-600 font-mono pt-2">{policy.policyNumber}</div>
                            </div>
                        </BentoBox>
                    ))}
                </div>
            </div>

            {/* SECTION 2: REGISTERED ACCOUNTS */}
            <div className="mb-8">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-gray-400 text-sm font-medium uppercase tracking-wider flex items-center gap-2">
                        <Lock size={16} /> Registered Accounts (Canada)
                    </h2>
                    <button onClick={() => setIsAccountModalOpen(true)} className="text-xs bg-white/5 hover:bg-white/10 text-white px-3 py-1.5 rounded flex items-center gap-1">
                        <Plus size={14} /> Add Account
                    </button>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {registeredAccounts.map(account => (
                        <BentoBox key={account.id}>
                            <div className="flex justify-between items-start mb-4">
                                <div>
                                    <div className="text-xl font-mono text-white tracking-tight">{account.type} <span className="text-gray-500 text-sm">/ {account.holder}</span></div>
                                    <div className="text-sm text-gray-400">{account.institution}</div>
                                </div>
                                <div className="text-2xl font-bold text-white">${account.currentValue.toLocaleString()}</div>
                            </div>

                            {account.contributionRoom > 0 && (
                                <div className="mt-4 bg-white/5 p-3 rounded-lg">
                                    <div className="flex justify-between text-xs mb-1">
                                        <span className="text-gray-400">Contribution Room Used</span>
                                        <span className="text-gray-300">${account.contributionRoom.toLocaleString()} Remaining</span>
                                    </div>
                                    {/* Pseudo-calc for room used vs total implicit */}
                                    <ProgressBar current={account.currentValue} max={account.currentValue + account.contributionRoom} color={account.type === 'TFSA' ? 'bg-electric-green' : 'bg-blue-500'} />
                                </div>
                            )}
                        </BentoBox>
                    ))}
                </div>
            </div>

            {/* SECTION 3: GOVERNMENT BENEFITS */}
            <div>
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-gray-400 text-sm font-medium uppercase tracking-wider flex items-center gap-2">
                        <CreditCard size={16} /> Government Benefits
                    </h2>
                    <button
                        onClick={() => {
                            setEditingBenefit(null);
                            setNewBenefit({
                                name: '',
                                benefit_type: 'CCB',
                                amount: 0,
                                frequency: 'MONTHLY',
                                government_agency: 'Government of Canada',
                                is_active: true
                            });
                            setIsGovBenefitModalOpen(true);
                        }}
                        className="text-xs bg-white/5 hover:bg-white/10 text-white px-3 py-1.5 rounded flex items-center gap-1"
                    >
                        <Plus size={14} /> Add Benefit
                    </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {govBenefits.length === 0 ? (
                        <div className="col-span-full text-center py-12 text-gray-500">
                            <CreditCard size={48} className="mx-auto mb-4 opacity-30" />
                            <p className="text-sm">No government benefits tracked yet.</p>
                            <p className="text-xs mt-2">Click "Add Benefit" to start tracking CCB, GST/HST, OAS, etc.</p>
                        </div>
                    ) : (
                        govBenefits.map(benefit => (
                            <BentoBox key={benefit.id} className="border-l-4 border-l-electric-green relative group">
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <div className="text-white font-bold">{benefit.name}</div>
                                        <div className="text-xs text-gray-500">{benefit.government_agency || 'Government Agency'}</div>
                                        {benefit.beneficiary && (
                                            <div className="text-xs text-gray-400 mt-1">Beneficiary: {benefit.beneficiary}</div>
                                        )}
                                    </div>
                                    <div className="text-right">
                                        <div className="text-xl font-mono text-electric-green">+${Number(benefit.amount).toFixed(2)}</div>
                                        <div className="text-xs text-gray-400">{benefit.frequency}</div>
                                    </div>
                                </div>
                                {benefit.next_payment_date && (
                                    <div className="mt-3 text-xs text-gray-500 bg-black/20 p-2 rounded">
                                        Next Deposit: <span className="text-gray-300">{new Date(benefit.next_payment_date).toLocaleDateString()}</span>
                                    </div>
                                )}
                                {benefit.notes && (
                                    <div className="mt-2 text-xs text-gray-400 italic">{benefit.notes}</div>
                                )}
                                {/* Action buttons - shown on hover */}
                                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
                                    <button
                                        onClick={() => handleEditBenefit(benefit)}
                                        className="bg-blue-500/80 hover:bg-blue-500 text-white p-1.5 rounded text-xs"
                                        title="Edit"
                                    >
                                        Edit
                                    </button>
                                    <button
                                        onClick={() => handleDeleteBenefit(benefit.id)}
                                        className="bg-red-500/80 hover:bg-red-500 text-white p-1.5 rounded text-xs"
                                        title="Delete"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </BentoBox>
                        ))
                    )}
                </div>
            </div>

            {/* MODAL: ADD INSURANCE */}
            <AnimatePresence>
                {isInsuranceModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setIsInsuranceModalOpen(false)} />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-finance-panel border border-grid-border rounded-2xl p-6 w-full max-w-md relative z-10 shadow-2xl"
                        >
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-xl font-bold text-white">Add Insurance Policy</h3>
                                <button onClick={() => setIsInsuranceModalOpen(false)} className="text-gray-400 hover:text-white"><X size={20} /></button>
                            </div>
                            <div className="space-y-4">
                                <input className="w-full bg-black/40 border border-grid-border rounded p-2 text-white" placeholder="Provider (e.g. Geico)" value={newPolicy.provider || ''} onChange={e => setNewPolicy({ ...newPolicy, provider: e.target.value })} />
                                <div className="grid grid-cols-2 gap-4">
                                    <select className="bg-black/40 border border-grid-border rounded p-2 text-white" value={newPolicy.type} onChange={e => setNewPolicy({ ...newPolicy, type: e.target.value as any })}><option value="Auto">Auto</option><option value="Home">Home</option><option value="Life">Life</option></select>
                                    <select className="bg-black/40 border border-grid-border rounded p-2 text-white" value={newPolicy.frequency} onChange={e => setNewPolicy({ ...newPolicy, frequency: e.target.value as any })}><option value="Monthly">Monthly</option><option value="Yearly">Yearly</option></select>
                                </div>
                                <input className="w-full bg-black/40 border border-grid-border rounded p-2 text-white" placeholder="Insured Item (e.g. 2023 Tesla)" value={newPolicy.insuredItem || ''} onChange={e => setNewPolicy({ ...newPolicy, insuredItem: e.target.value })} />
                                <div className="grid grid-cols-2 gap-4">
                                    <input type="number" className="bg-black/40 border border-grid-border rounded p-2 text-white" placeholder="Premium $" value={newPolicy.premium || ''} onChange={e => setNewPolicy({ ...newPolicy, premium: Number(e.target.value) })} />
                                    <input type="date" className="bg-black/40 border border-grid-border rounded p-2 text-white" value={newPolicy.renewalDate || ''} onChange={e => setNewPolicy({ ...newPolicy, renewalDate: e.target.value })} />
                                </div>
                                <button onClick={handleAddPolicy} className="w-full bg-neon-purple text-white font-bold py-3 rounded-xl mt-2">Save Policy</button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* MODAL: ADD ACCOUNT */}
            <AnimatePresence>
                {isAccountModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setIsAccountModalOpen(false)} />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-finance-panel border border-grid-border rounded-2xl p-6 w-full max-w-md relative z-10 shadow-2xl"
                        >
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-xl font-bold text-white">Add Registered Account</h3>
                                <button onClick={() => setIsAccountModalOpen(false)} className="text-gray-400 hover:text-white"><X size={20} /></button>
                            </div>
                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <select className="bg-black/40 border border-grid-border rounded p-2 text-white" value={newAccount.type} onChange={e => setNewAccount({ ...newAccount, type: e.target.value as any })}><option value="TFSA">TFSA</option><option value="RRSP">RRSP</option><option value="RESP">RESP</option><option value="FHSA">FHSA</option></select>
                                    <input className="bg-black/40 border border-grid-border rounded p-2 text-white" placeholder="Holder (Mom/Dad)" value={newAccount.holder || ''} onChange={e => setNewAccount({ ...newAccount, holder: e.target.value })} />
                                </div>
                                <input className="w-full bg-black/40 border border-grid-border rounded p-2 text-white" placeholder="Institution (e.g. Questrade)" value={newAccount.institution || ''} onChange={e => setNewAccount({ ...newAccount, institution: e.target.value })} />
                                <div className="grid grid-cols-2 gap-4">
                                    <input type="number" className="bg-black/40 border border-grid-border rounded p-2 text-white" placeholder="Current Value" value={newAccount.currentValue || ''} onChange={e => setNewAccount({ ...newAccount, currentValue: Number(e.target.value) })} />
                                    <input type="number" className="bg-black/40 border border-grid-border rounded p-2 text-white" placeholder="Available Room" value={newAccount.contributionRoom || ''} onChange={e => setNewAccount({ ...newAccount, contributionRoom: Number(e.target.value) })} />
                                </div>
                                <button onClick={handleAddAccount} className="w-full bg-neon-purple text-white font-bold py-3 rounded-xl mt-2">Save Account</button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* MODAL: ADD/EDIT GOVERNMENT BENEFIT */}
            <AnimatePresence>
                {isGovBenefitModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={() => setIsGovBenefitModalOpen(false)} />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-finance-panel border border-grid-border rounded-2xl p-6 w-full max-w-lg relative z-10 shadow-2xl max-h-[90vh] overflow-y-auto"
                        >
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-xl font-bold text-white">{editingBenefit ? 'Edit' : 'Add'} Government Benefit</h3>
                                <button onClick={() => setIsGovBenefitModalOpen(false)} className="text-gray-400 hover:text-white"><X size={20} /></button>
                            </div>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-xs text-gray-400 mb-1 block">Benefit Name *</label>
                                    <input
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                        placeholder="e.g., CCB (Child Benefit)"
                                        value={newBenefit.name || ''}
                                        onChange={e => setNewBenefit({ ...newBenefit, name: e.target.value })}
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-xs text-gray-400 mb-1 block">Benefit Type *</label>
                                        <select
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                            value={newBenefit.benefit_type}
                                            onChange={e => setNewBenefit({ ...newBenefit, benefit_type: e.target.value })}
                                        >
                                            <option value="CCB">CCB (Child Benefit)</option>
                                            <option value="GST">GST/HST Credit</option>
                                            <option value="OAS">OAS (Old Age Security)</option>
                                            <option value="CPP">CPP (Canada Pension)</option>
                                            <option value="EI">EI (Employment Insurance)</option>
                                            <option value="OTHER">Other</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="text-xs text-gray-400 mb-1 block">Frequency *</label>
                                        <select
                                            className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                            value={newBenefit.frequency}
                                            onChange={e => setNewBenefit({ ...newBenefit, frequency: e.target.value })}
                                        >
                                            <option value="WEEKLY">Weekly</option>
                                            <option value="BIWEEKLY">Bi-weekly</option>
                                            <option value="MONTHLY">Monthly</option>
                                            <option value="QUARTERLY">Quarterly</option>
                                            <option value="SEMI_ANNUALLY">Semi-annually</option>
                                            <option value="ANNUALLY">Annually</option>
                                        </select>
                                    </div>
                                </div>
                                <div>
                                    <label className="text-xs text-gray-400 mb-1 block">Amount (per payment) *</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                        placeholder="450.00"
                                        value={newBenefit.amount || ''}
                                        onChange={e => setNewBenefit({ ...newBenefit, amount: Number(e.target.value) })}
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-gray-400 mb-1 block">Government Agency</label>
                                    <input
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                        placeholder="e.g., Government of Canada, CRA"
                                        value={newBenefit.government_agency || ''}
                                        onChange={e => setNewBenefit({ ...newBenefit, government_agency: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-gray-400 mb-1 block">Beneficiary</label>
                                    <input
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                        placeholder="e.g., Family, John Doe"
                                        value={newBenefit.beneficiary || ''}
                                        onChange={e => setNewBenefit({ ...newBenefit, beneficiary: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-gray-400 mb-1 block">Next Payment Date</label>
                                    <input
                                        type="date"
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                        value={newBenefit.next_payment_date || ''}
                                        onChange={e => setNewBenefit({ ...newBenefit, next_payment_date: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-gray-400 mb-1 block">Notes</label>
                                    <textarea
                                        className="w-full bg-black/40 border border-grid-border rounded p-2 text-white"
                                        rows={3}
                                        placeholder="Additional notes or details..."
                                        value={newBenefit.notes || ''}
                                        onChange={e => setNewBenefit({ ...newBenefit, notes: e.target.value })}
                                    />
                                </div>
                                <div className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        id="is_active"
                                        checked={newBenefit.is_active}
                                        onChange={e => setNewBenefit({ ...newBenefit, is_active: e.target.checked })}
                                        className="w-4 h-4"
                                    />
                                    <label htmlFor="is_active" className="text-sm text-gray-300">Active (currently receiving this benefit)</label>
                                </div>
                                <button onClick={handleAddOrUpdateBenefit} className="w-full bg-electric-green hover:bg-green-500 text-black font-bold py-3 rounded-xl mt-2">
                                    {editingBenefit ? 'Update' : 'Save'} Benefit
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

        </div>
    );
};

