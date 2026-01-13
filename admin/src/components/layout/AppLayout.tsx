import React, { useState } from 'react';
import { Sidebar } from './Sidebar';

interface AppLayoutProps {
    children: React.ReactNode;
    activeView: string;
    onNavigate: (view: string) => void;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children, activeView, onNavigate }) => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <div className="flex h-screen w-screen bg-finance-black text-white overflow-hidden">
            <Sidebar
                activeView={activeView}
                onNavigate={onNavigate}
                isCollapsed={isCollapsed}
                toggleCollapse={() => setIsCollapsed(!isCollapsed)}
            />
            <main className="flex-1 overflow-auto relative p-0 bg-finance-black">
                {/* Background Grid Pattern */}
                <div className="absolute inset-0 z-0 pointer-events-none opacity-[0.03]"
                    style={{
                        backgroundImage: 'linear-gradient(to right, #ffffff 1px, transparent 1px), linear-gradient(to bottom, #ffffff 1px, transparent 1px)',
                        backgroundSize: '40px 40px'
                    }}
                />
                <div className="relative z-10 h-full">
                    {children}
                </div>
            </main>
        </div>
    );
};
