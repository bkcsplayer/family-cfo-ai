import { useState } from 'react';
import { AppLayout } from './components/layout/AppLayout';
import { Dashboard } from './views/Dashboard';
import { TransactionReview } from './views/TransactionReview';
import { MonthlyReport } from './views/MonthlyReport';
import { AssetHub } from './views/AssetHub';
import { BenefitsLocker } from './views/BenefitsLocker';
import { BudgetManager } from './views/BudgetManager';
import { Login } from './views/Login';
import { AdminSettings } from './views/AdminSettings';
import { PendingReviews } from './views/PendingReviews';
import { StoreProvider } from './context/StoreContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ViewNavigationProvider } from './context/ViewNavigationContext';

const AppContent = () => {
  const { isAuthenticated, loading } = useAuth();
  const [activeView, setActiveView] = useState('dashboard');

  if (loading) {
    return (
      <div className="h-screen w-full bg-finance-black flex items-center justify-center">
        <div className="text-neon-purple">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  const renderView = () => {
    switch (activeView) {
      case 'dashboard': return <Dashboard />;
      case 'transactions': return <TransactionReview />;
      case 'monthly-report': return <MonthlyReport />;
      case 'assets': return <AssetHub />;
      case 'benefits': return <BenefitsLocker />;
      case 'budgets': return <BudgetManager />;
      case 'reviews': return <PendingReviews />;
      case 'settings': return <AdminSettings />;
      default: return <Dashboard />;
    }
  };

  return (
    <ViewNavigationProvider navigateTo={setActiveView}>
      <AppLayout activeView={activeView} onNavigate={setActiveView}>
        {renderView()}
      </AppLayout>
    </ViewNavigationProvider>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <StoreProvider>
        <AppContent />
      </StoreProvider>
    </AuthProvider>
  );
}
