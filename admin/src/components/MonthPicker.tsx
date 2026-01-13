import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import { motion } from 'framer-motion';

interface MonthPickerProps {
    selectedMonth: string; // Format: "YYYY-MM"
    onChange: (month: string) => void;
    compact?: boolean;
}

export const MonthPicker = ({ selectedMonth, onChange, compact = false }: MonthPickerProps) => {
    const currentDate = new Date(selectedMonth + '-01');
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const monthNames = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];

    const goToPreviousMonth = () => {
        const newDate = new Date(year, month - 1, 1);
        const newMonth = `${newDate.getFullYear()}-${String(newDate.getMonth() + 1).padStart(2, '0')}`;
        onChange(newMonth);
    };

    const goToNextMonth = () => {
        const newDate = new Date(year, month + 1, 1);
        const newMonth = `${newDate.getFullYear()}-${String(newDate.getMonth() + 1).padStart(2, '0')}`;
        onChange(newMonth);
    };

    const goToCurrentMonth = () => {
        const now = new Date();
        const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
        onChange(currentMonth);
    };

    // Check if current month is selected
    const now = new Date();
    const isCurrentMonth = selectedMonth === `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;

    if (compact) {
        return (
            <div className="flex items-center gap-2">
                <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={goToPreviousMonth}
                    className="p-1.5 rounded-lg bg-finance-panel border border-grid-border hover:border-neon-purple/50 transition-colors"
                >
                    <ChevronLeft size={16} className="text-gray-400" />
                </motion.button>

                <div className="px-3 py-1.5 rounded-lg bg-finance-panel border border-grid-border flex items-center gap-2 min-w-[100px] justify-center">
                    <Calendar size={14} className="text-neon-purple" />
                    <span className="text-sm font-medium text-white">
                        {monthNames[month]} {year}
                    </span>
                </div>

                <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={goToNextMonth}
                    className="p-1.5 rounded-lg bg-finance-panel border border-grid-border hover:border-neon-purple/50 transition-colors"
                >
                    <ChevronRight size={16} className="text-gray-400" />
                </motion.button>

                {!isCurrentMonth && (
                    <motion.button
                        whileTap={{ scale: 0.95 }}
                        onClick={goToCurrentMonth}
                        className="px-2 py-1.5 rounded-lg bg-neon-purple/20 border border-neon-purple/50 text-xs text-neon-purple hover:bg-neon-purple/30 transition-colors"
                    >
                        Today
                    </motion.button>
                )}
            </div>
        );
    }

    return (
        <div className="flex items-center justify-between bg-finance-panel border border-grid-border rounded-xl p-3">
            <motion.button
                whileTap={{ scale: 0.95 }}
                onClick={goToPreviousMonth}
                className="p-2 rounded-lg hover:bg-white/5 transition-colors"
            >
                <ChevronLeft size={20} className="text-gray-400" />
            </motion.button>

            <div className="flex items-center gap-3">
                <Calendar size={18} className="text-neon-purple" />
                <div className="text-center">
                    <div className="text-lg font-medium text-white">{monthNames[month]} {year}</div>
                    <div className="text-xs text-gray-500">Filter by month</div>
                </div>
            </div>

            <motion.button
                whileTap={{ scale: 0.95 }}
                onClick={goToNextMonth}
                className="p-2 rounded-lg hover:bg-white/5 transition-colors"
            >
                <ChevronRight size={20} className="text-gray-400" />
            </motion.button>

            {!isCurrentMonth && (
                <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={goToCurrentMonth}
                    className="ml-2 px-3 py-1.5 rounded-lg bg-neon-purple/20 border border-neon-purple/50 text-sm text-neon-purple hover:bg-neon-purple/30 transition-colors"
                >
                    Current Month
                </motion.button>
            )}
        </div>
    );
};
