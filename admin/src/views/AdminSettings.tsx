import React, { useState } from 'react';
import { useStore, type User } from '../context/StoreContext';
import { useAuth } from '../context/AuthContext';
import { BentoBox } from '../components/ui/BentoBox';
import { Shield, Users, UserPlus, X, Copy, Check, LogOut } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const AdminSettings: React.FC = () => {
    const { users, actions } = useStore();
    const { user: currentUser, logout } = useAuth();
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [newUser, setNewUser] = useState<Partial<User>>({ role: 'Viewer', status: 'Active' });
    const [createdCredentials, setCreatedCredentials] = useState<{ username: string, pass: string } | null>(null);

    // Only Admin can see this page content
    if (currentUser?.role !== 'Admin') {
        return (
            <div className="h-full flex items-center justify-center text-gray-500">
                <Shield className="mr-2" /> Access Restricted: Administrators Only
            </div>
        );
    }

    const handleCreateUser = () => {
        if (!newUser.username || !newUser.displayName) return;

        actions.addUser(newUser as any);
        // Mock password generation for "Copy Credentials" feature
        setCreatedCredentials({
            username: newUser.username,
            pass: Math.random().toString(36).slice(-8).toUpperCase()
        });
        setNewUser({ role: 'Viewer', status: 'Active' });
        // Don't close modal yet, show credentials first
    };

    const closeAndReset = () => {
        setIsAddModalOpen(false);
        setCreatedCredentials(null);
    };

    return (
        <div className="p-8 h-full overflow-y-auto">
            <header className="mb-8 flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-light text-white mb-2 tracking-tight">System <span className="text-gray-500">Settings</span></h1>
                    <p className="text-gray-500 text-sm">Access Control & Staff Management</p>
                </div>
                <button
                    onClick={logout}
                    className="bg-white/5 hover:bg-white/10 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors border border-white/10"
                >
                    <LogOut size={18} />
                    <span>Logout</span>
                </button>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Staff List */}
                <BentoBox title="Staff & Access Control" className="lg:col-span-2">
                    <div className="flex justify-end mb-4">
                        <button
                            onClick={() => setIsAddModalOpen(true)}
                            className="bg-white/5 hover:bg-white/10 text-white text-xs px-3 py-1.5 rounded flex items-center gap-2 transition-colors border border-white/10"
                        >
                            <UserPlus size={14} /> Issue New Access
                        </button>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="text-xs text-gray-500 border-b border-white/10">
                                    <th className="pb-3 pl-2">User</th>
                                    <th className="pb-3">Role</th>
                                    <th className="pb-3">Status</th>
                                    <th className="pb-3 text-right pr-2">Last Login</th>
                                </tr>
                            </thead>
                            <tbody className="text-sm">
                                {users.map(user => (
                                    <tr key={user.id} className="border-b border-white/5 hover:bg-white/5 transition-colors group">
                                        <td className="py-3 pl-2">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-700 to-black flex items-center justify-center text-xs font-bold text-gray-300 border border-white/10">
                                                    {user.displayName.charAt(0)}
                                                </div>
                                                <div>
                                                    <div className="text-white font-medium">{user.displayName}</div>
                                                    <div className="text-xs text-gray-500 font-mono">@{user.username}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="py-3">
                                            <span className={`text-xs px-2 py-1 rounded border ${user.role === 'Admin' ? 'bg-neon-purple/10 border-neon-purple/20 text-neon-purple' :
                                                user.role === 'Editor' ? 'bg-blue-500/10 border-blue-500/20 text-blue-400' :
                                                    'bg-gray-700/30 border-gray-600 text-gray-400'
                                                }`}>
                                                {user.role}
                                            </span>
                                        </td>
                                        <td className="py-3">
                                            <div className="flex items-center gap-1.5">
                                                <div className={`w-1.5 h-1.5 rounded-full ${user.status === 'Active' ? 'bg-electric-green shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-gray-600'}`} />
                                                <span className="text-gray-400 text-xs">{user.status}</span>
                                            </div>
                                        </td>
                                        <td className="py-3 text-right pr-2 text-gray-500 text-xs font-mono">
                                            {user.lastLogin || 'Never'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </BentoBox>

                {/* Role Definitions */}
                <div className="space-y-6">
                    <BentoBox title="Role Definitions">
                        <div className="space-y-4">
                            <div className="flex gap-3">
                                <div className="mt-1"><Shield size={16} className="text-neon-purple" /></div>
                                <div>
                                    <h4 className="text-white text-sm font-bold">Admin</h4>
                                    <p className="text-xs text-gray-500 leading-relaxed">Full system access. Can manage users, approve heavy transactions, and view all hidden assets.</p>
                                </div>
                            </div>
                            <div className="flex gap-3">
                                <div className="mt-1"><Users size={16} className="text-blue-400" /></div>
                                <div>
                                    <h4 className="text-white text-sm font-bold">Editor</h4>
                                    <p className="text-xs text-gray-500 leading-relaxed">Can add receipts, categorize transactions, and request approvals. Cannot manage users.</p>
                                </div>
                            </div>
                            <div className="flex gap-3">
                                <div className="mt-1"><Users size={16} className="text-gray-500" /></div>
                                <div>
                                    <h4 className="text-white text-sm font-bold">Viewer</h4>
                                    <p className="text-xs text-gray-500 leading-relaxed">Read-only access to Dashboards and Reports. Cannot edit data.</p>
                                </div>
                            </div>
                        </div>
                    </BentoBox>
                </div>
            </div>

            {/* ADD USER MODAL */}
            <AnimatePresence>
                {isAddModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                            onClick={closeAndReset}
                        />
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-finance-panel border border-grid-border rounded-2xl p-6 w-full max-w-md relative z-10 shadow-2xl"
                        >
                            {!createdCredentials ? (
                                <>
                                    <div className="flex justify-between items-center mb-6">
                                        <h3 className="text-xl font-bold text-white">Issue Staff Access</h3>
                                        <button onClick={closeAndReset} className="text-gray-400 hover:text-white"><X size={20} /></button>
                                    </div>
                                    <div className="space-y-4">
                                        <input
                                            className="w-full bg-black/40 border border-grid-border rounded p-3 text-white focus:border-neon-purple/50 outline-none transition-colors"
                                            placeholder="Display Name (e.g. Partner)"
                                            value={newUser.displayName || ''}
                                            onChange={e => setNewUser({ ...newUser, displayName: e.target.value })}
                                        />
                                        <input
                                            className="w-full bg-black/40 border border-grid-border rounded p-3 text-white focus:border-neon-purple/50 outline-none transition-colors"
                                            placeholder="Username (e.g. partner)"
                                            value={newUser.username || ''}
                                            onChange={e => setNewUser({ ...newUser, username: e.target.value })}
                                        />
                                        <select
                                            className="w-full bg-black/40 border border-grid-border rounded p-3 text-white focus:border-neon-purple/50 outline-none transition-colors"
                                            value={newUser.role}
                                            onChange={e => setNewUser({ ...newUser, role: e.target.value as any })}
                                        >
                                            <option value="Viewer">Viewer (Read Only)</option>
                                            <option value="Editor">Editor (Can Upload)</option>
                                            <option value="Admin">Admin (Full Access)</option>
                                        </select>

                                        <button onClick={handleCreateUser} className="w-full bg-white text-black font-bold py-3 rounded-xl mt-2 hover:bg-gray-200 transition-colors">
                                            Generate Credentials
                                        </button>
                                    </div>
                                </>
                            ) : (
                                <div className="text-center py-4">
                                    <div className="w-16 h-16 bg-electric-green/10 rounded-full flex items-center justify-center mx-auto mb-4 text-electric-green">
                                        <Check size={32} />
                                    </div>
                                    <h3 className="text-xl font-bold text-white mb-2">Access Issued</h3>
                                    <p className="text-sm text-gray-500 mb-6">Share these credentials securely.</p>

                                    <div className="bg-black/50 border border-white/10 rounded-xl p-4 mb-6 text-left space-y-2 font-mono text-sm relative group cursor-pointer" onClick={() => { navigator.clipboard.writeText(`User: ${createdCredentials.username}\nPass: ${createdCredentials.pass}`) }}>
                                        <div className="flex justify-between text-gray-400">
                                            <span>Username:</span>
                                            <span className="text-white">{createdCredentials.username}</span>
                                        </div>
                                        <div className="flex justify-between text-gray-400">
                                            <span>Password:</span>
                                            <span className="text-white">{createdCredentials.pass}</span>
                                        </div>
                                        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <Copy size={14} className="text-gray-500" />
                                        </div>
                                    </div>

                                    <button onClick={closeAndReset} className="w-full bg-white/10 text-white font-bold py-3 rounded-xl hover:bg-white/20 transition-colors">
                                        Done
                                    </button>
                                </div>
                            )}
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};
