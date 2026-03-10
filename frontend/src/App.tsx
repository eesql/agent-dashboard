/**
 * 应用主组件
 */
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { ThemeProvider } from '@/context/ThemeContext';
import { ThemeToggle } from '@/components/layout/ThemeToggle';
import { Dashboard } from '@/pages/Dashboard';
import { Sessions } from '@/pages/Sessions';
import { SessionDetail } from '@/pages/SessionDetail';

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-bg-primary">
          {/* 顶部导航栏 */}
          <header className="border-b border-border-default bg-bg-secondary sticky top-0 z-50">
            <div className="container mx-auto px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-sm">AD</span>
                  </div>
                  <h1 className="text-xl font-bold text-text-primary">
                    Agent Dashboard
                  </h1>
                </div>
                <div className="flex items-center gap-6">
                  <NavLinks />
                  <ThemeToggle />
                  <a 
                    href="/docs" 
                    target="_blank"
                    className="text-sm text-text-secondary hover:text-primary-500 transition-colors"
                  >
                    API Docs
                  </a>
                </div>
              </div>
            </div>
          </header>

          {/* 主内容区 */}
          <main className="container mx-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/sessions" element={<Sessions />} />
              <Route path="/sessions/:sessionId" element={<SessionDetail />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
};

// 导航链接组件
const NavLinks: React.FC = () => {
  const location = useLocation();
  
  const links = [
    { path: '/', label: 'Dashboard' },
    { path: '/sessions', label: 'Sessions' },
  ];
  
  return (
    <nav className="flex items-center gap-1">
      {links.map(link => (
        <Link
          key={link.path}
          to={link.path}
          className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
            location.pathname === link.path
              ? 'bg-primary-500/10 text-primary-500'
              : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary'
          }`}
        >
          {link.label}
        </Link>
      ))}
    </nav>
  );
};

export default App;
