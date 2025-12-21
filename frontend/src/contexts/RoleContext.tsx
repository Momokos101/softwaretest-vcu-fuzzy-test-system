import { createContext, useContext, useState, ReactNode } from 'react';

export type UserRole = 'test_engineer' | 'process_engineer' | 'maintenance_engineer';

interface RoleContextType {
  currentRole: UserRole;
  setCurrentRole: (role: UserRole) => void;
  roleName: string;
  roleColor: string;
}

const RoleContext = createContext<RoleContextType | undefined>(undefined);

const roleConfig = {
  test_engineer: {
    name: '测试工程师',
    color: 'blue',
  },
  process_engineer: {
    name: '工艺工程师',
    color: 'green',
  },
  maintenance_engineer: {
    name: '台架维护工程师',
    color: 'orange',
  },
};

export function RoleProvider({ children }: { children: ReactNode }) {
  const [currentRole, setCurrentRole] = useState<UserRole>('test_engineer');

  const config = roleConfig[currentRole];

  return (
    <RoleContext.Provider
      value={{
        currentRole,
        setCurrentRole,
        roleName: config.name,
        roleColor: config.color,
      }}
    >
      {children}
    </RoleContext.Provider>
  );
}

export function useRole() {
  const context = useContext(RoleContext);
  if (!context) {
    throw new Error('useRole must be used within RoleProvider');
  }
  return context;
}

