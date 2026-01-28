/**
 * Main App component with routing.
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import MarketAnalysis from './pages/MarketAnalysis';
import AIChat from './components/AIChat';

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex space-x-8">
                <Link
                  to="/"
                  className="text-gray-900 hover:text-primary-600 px-3 py-2 text-sm font-medium"
                >
                  Properties
                </Link>
                <Link
                  to="/market-analysis"
                  className="text-gray-900 hover:text-primary-600 px-3 py-2 text-sm font-medium"
                >
                  Market Analysis
                </Link>
                <Link
                  to="/ai-assistant"
                  className="text-gray-900 hover:text-primary-600 px-3 py-2 text-sm font-medium"
                >
                  AI Assistant
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/market-analysis" element={<MarketAnalysis />} />
          <Route
            path="/ai-assistant"
            element={
              <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
                <AIChat />
              </div>
            }
          />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
