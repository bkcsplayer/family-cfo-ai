import React from 'react';
import { clsx } from 'clsx';

interface BentoBoxProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
    className?: string;
    title?: string;
    action?: React.ReactNode;
}

export const BentoBox: React.FC<BentoBoxProps> = ({ children, className, title, action, ...props }) => {
    return (
        <div
            className={clsx(
                "bg-finance-panel border border-grid-border rounded-2xl p-6 flex flex-col",
                className
            )}
            {...props}
        >
            {(title || action) && (
                <div className="flex justify-between items-center mb-4">
                    {title && <h3 className="text-gray-400 font-medium text-sm tracking-wide uppercase">{title}</h3>}
                    {action && <div>{action}</div>}
                </div>
            )}
            <div className="flex-1 relative">
                {children}
            </div>
        </div>
    );
};
