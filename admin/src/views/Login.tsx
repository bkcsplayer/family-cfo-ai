import React, { useState } from 'react';
import { Lock, ArrowRight, ShieldCheck, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';

export const Login: React.FC = () => {
    const { login } = useAuth();
    const [username, setUsername] = useState('admin');
    const [password, setPassword] = useState('admin123');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            await login(username, password);
            // Success - AuthContext will update user state and App will re-render
        } catch (err: any) {
            setError(err.message || 'Access Denied: Invalid Credentials');
            setIsLoading(false);
        }
    };

    return (
        <div className="h-screen w-full bg-black flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-neon-purple/20 blur-[150px] rounded-full pointer-events-none" />
            <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-blue-600/10 blur-[150px] rounded-full pointer-events-none" />

            <div className="w-full max-w-md relative z-10">
                <div className="mb-10 text-center">
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-white/5 border border-white/10 mb-6 shadow-2xl shadow-neon-purple/20"
                    >
                        <ShieldCheck size={32} className="text-neon-purple" />
                    </motion.div>
                    <motion.h1
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.2 }}
                        className="text-4xl font-bold text-white tracking-tighter mb-2"
                    >
                        Family Inc. <span className="text-neon-purple drop-shadow-[0_0_15px_rgba(168,85,247,0.5)]">CFO</span>
                    </motion.h1>
                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                        className="text-gray-500 text-sm uppercase tracking-widest"
                    >
                        Secure Financial Terminal
                    </motion.p>
                </div>

                <motion.form
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.4 }}
                    onSubmit={handleLogin}
                    className="space-y-4"
                >
                    <div className="group">
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500 group-focus-within:text-neon-purple transition-colors">
                                <Lock size={18} />
                            </div>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-12 pr-4 text-white placeholder-gray-600 focus:outline-none focus:border-neon-purple/50 focus:bg-white/10 transition-all"
                                placeholder="Operator ID"
                            />
                        </div>
                    </div>

                    <div className="group">
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full bg-white/5 border border-white/10 rounded-xl py-4 px-4 text-center text-white placeholder-gray-600 focus:outline-none focus:border-neon-purple/50 focus:bg-white/10 transition-all tracking-widest"
                            placeholder="••••••••"
                        />
                    </div>

                    <AnimatePresence>
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="text-red-400 text-xs text-center bg-red-500/10 py-2 rounded border border-red-500/20"
                            >
                                {error}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <button
                        disabled={isLoading}
                        className="w-full bg-white text-black font-bold py-4 rounded-xl hover:bg-gray-200 transition-colors flex items-center justify-center gap-2 group disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                        {isLoading ? (
                            <>
                                <Loader2 size={18} className="animate-spin" />
                                <span className="text-xs uppercase tracking-wide">Decrypting Ledger...</span>
                            </>
                        ) : (
                            <>
                                <span>Authenticate</span>
                                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                            </>
                        )}
                    </button>
                </motion.form>

                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.8 }}
                    className="mt-12 text-center"
                >
                    <p className="text-[10px] text-gray-700 font-mono">
                        SYSTEM ACCESS RESTRICTED • ENCRYPTION LEVEL 1
                    </p>
                </motion.div>
            </div>
        </div>
    );
};
