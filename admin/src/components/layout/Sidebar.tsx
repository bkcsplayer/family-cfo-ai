import React from 'react';
import {
    LayoutDashboard,
    FileText,
    Building2,
    Heart,
    ChevronLeft,
    ChevronRight,
    Settings,
    Smartphone,
    PiggyBank,
    FileCheck,
    TrendingUp
} from 'lucide-react';
import { clsx } from 'clsx';
import { motion } from 'framer-motion';

interface SidebarProps {
    activeView: string;
    onNavigate: (view: string) => void;
    isCollapsed: boolean;
    toggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeView, onNavigate, isCollapsed, toggleCollapse }) => {
    const navItems = [
        { id: 'dashboard', label: 'Cockpit', icon: LayoutDashboard },
        { id: 'transactions', label: 'Review Workbench', icon: FileText },
        { id: 'monthly-report', label: 'Monthly Report', icon: TrendingUp },
        { id: 'assets', label: 'Asset Hub', icon: Building2 },
        { id: 'benefits', label: 'Benefits & Equity', icon: Heart },
        { id: 'budgets', label: 'Budget Manager', icon: PiggyBank },
        { id: 'reviews', label: 'Document Reviews', icon: FileCheck },
        { id: 'mobile', label: 'Mobile App Sim', icon: Smartphone },
    ];

    return (
        <motion.div
            animate={{ width: isCollapsed ? 80 : 280 }}
            className="h-screen bg-finance-panel border-r border-grid-border flex flex-col transition-all duration-300 relative z-20"
        >
            {/* Header */}
            <div className="h-16 flex items-center px-6 border-b border-grid-border">
                <div className={clsx("font-bold text-xl tracking-tighter text-white whitespace-nowrap overflow-hidden flex items-center gap-2", isCollapsed && "justify-center")}>
                    <div className="w-8 h-8 rounded bg-neon-purple flex items-center justify-center text-white shrink-0">
                        F
                    </div>
                    {!isCollapsed && <span className="text-gray-100">FAMILY INC.</span>}
                </div>
            </div>

            {/* Navigation */}
            <div className="flex-1 py-6 flex flex-col gap-2 px-3">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeView === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => onNavigate(item.id)}
                            className={clsx(
                                "flex items-center gap-3 px-3 py-3 rounded-lg transition-all group relative overflow-hidden",
                                isActive
                                    ? "bg-neon-purple/10 text-neon-purple"
                                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                            )}
                        >
                            {isActive && (
                                <div className="absolute left-0 top-0 bottom-0 w-1 bg-neon-purple rounded-full" />
                            )}
                            <Icon size={20} className="shrink-0" />
                            {!isCollapsed && (
                                <span className="font-medium whitespace-nowrap">
                                    {item.label}
                                </span>
                            )}

                            {/* Tooltip for collapsed mode */}
                            {isCollapsed && (
                                <div className="absolute left-full ml-4 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 whitespace-nowrap pointer-events-none z-50">
                                    {item.label}
                                </div>
                            )}
                        </button>
                    );
                })}
            </div>

            {/* Footer / User */}
            <div className="p-4 border-t border-grid-border">
                <button
                    onClick={() => onNavigate('settings')}
                    className={clsx(
                        "flex items-center gap-3 w-full transition-colors",
                        activeView === 'settings' ? "text-neon-purple" : "text-gray-400 hover:text-white"
                    )}
                >
                    <Settings size={20} />
                    {!isCollapsed && <span>Settings</span>}
                </button>
            </div>

            {/* Collapse Toggle */}
            <button
                onClick={toggleCollapse}
                className="absolute -right-3 top-20 w-6 h-6 bg-finance-panel border border-grid-border rounded-full flex items-center justify-center text-gray-400 hover:text-white"
            >
                {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
            </button>
        </motion.div>
    );
};
