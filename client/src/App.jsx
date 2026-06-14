import React, { useState, useEffect } from 'react';
import { ConfigProvider, theme, App as AntApp } from 'antd';
import Auth from './components/Auth';
import Dashboard from './components/Dashboard';
import VideoDetail from './components/VideoDetail';

function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [currentView, setCurrentView] = useState('auth');
  const [activeVideoId, setActiveVideoId] = useState(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      setCurrentView('dashboard');
    }

    const handleAuthError = () => {
      handleLogout();
    };

    window.addEventListener('auth-error', handleAuthError);
    return () => window.removeEventListener('auth-error', handleAuthError);
  }, []);

  const handleAuthSuccess = (userProfile, accessToken) => {
    setUser(userProfile);
    setToken(accessToken);
    setCurrentView('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setToken(null);
    setActiveVideoId(null);
    setCurrentView('auth');
  };

  const handleViewVideo = (videoId) => {
    setActiveVideoId(videoId);
    setCurrentView('detail');
  };

  const handleBackToDashboard = () => {
    setActiveVideoId(null);
    setCurrentView('dashboard');
  };

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#8b5cf6', // Violet 500
          colorBgBase: '#0b0f19', // Obsidian background
          colorBgContainer: '#111827', // Card dark background
          colorBorder: 'rgba(255, 255, 255, 0.08)',
          borderRadius: 8,
        },
      }}
    >
      <AntApp>
        <div className="min-h-screen text-gray-200">
          {currentView === 'auth' && (
            <Auth onAuthSuccess={handleAuthSuccess} />
          )}
          
          {currentView === 'dashboard' && (
            <Dashboard 
              user={user} 
              onLogout={handleLogout} 
              onViewVideo={handleViewVideo} 
            />
          )}
          
          {currentView === 'detail' && (
            <VideoDetail 
              videoId={activeVideoId} 
              onBack={handleBackToDashboard} 
            />
          )}
        </div>
      </AntApp>
    </ConfigProvider>
  );
}

export default App;
