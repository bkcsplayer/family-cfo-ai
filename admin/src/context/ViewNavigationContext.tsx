import React, { createContext, useContext } from 'react';

interface ViewNavigationContextType {
    navigateTo: (view: string) => void;
}

const ViewNavigationContext = createContext<ViewNavigationContextType | undefined>(undefined);

export const ViewNavigationProvider: React.FC<{ navigateTo: (view: string) => void; children: React.ReactNode }> = ({ navigateTo, children }) => {
    return (
        <ViewNavigationContext.Provider value={{ navigateTo }}>
            {children}
        </ViewNavigationContext.Provider>
    );
};

export const useViewNavigation = () => {
    const context = useContext(ViewNavigationContext);
    if (!context) {
        throw new Error('useViewNavigation must be used within ViewNavigationProvider');
    }
    return context;
};
