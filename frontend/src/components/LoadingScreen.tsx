import React from 'react';
import { Loader2, Database, Zap } from 'lucide-react';

interface LoadingScreenProps {
  message: string;
  backendStatus?: {
    connected: boolean;
    port: number;
    processRunning: boolean;
  } | null;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ message, backendStatus }) => {
  return (
    <div className="loading-screen">
      <div className="text-center space-y-6">
        {/* Logo/Icon */}
        <div className="flex justify-center">
          <div className="relative">
            <Database className="w-20 h-20 text-blue-400" />
            <Zap className="w-8 h-8 text-yellow-400 absolute -top-2 -right-2" />
          </div>
        </div>
        
        {/* Title */}
        <h1 className="text-4xl font-bold text-white">
          Unified Data Studio v2
        </h1>
        
        {/* Subtitle */}
        <p className="text-xl text-blue-100">
          Next-generation data management platform
        </p>
        
        {/* Loading Message */}
        <div className="flex items-center justify-center space-x-3">
          <Loader2 className="w-6 h-6 animate-spin text-blue-300" />
          <span className="text-lg text-white">{message}</span>
        </div>
        
        {/* Backend Status */}
        {backendStatus && (
          <div className="mt-8 p-4 bg-white/10 rounded-lg backdrop-blur-sm">
            <h3 className="text-lg font-semibold text-white mb-2">Backend Status</h3>
            <div className="space-y-2 text-sm text-blue-100">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${backendStatus.processRunning ? 'bg-green-400' : 'bg-red-400'}`} />
                <span>Process: {backendStatus.processRunning ? 'Running' : 'Stopped'}</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${backendStatus.connected ? 'bg-green-400' : 'bg-yellow-400'}`} />
                <span>Connection: {backendStatus.connected ? 'Connected' : 'Connecting...'}</span>
              </div>
              <div className="text-xs text-blue-200">
                Port: {backendStatus.port}
              </div>
            </div>
          </div>
        )}
        
        {/* Loading Animation */}
        <div className="mt-8">
          <div className="flex space-x-2">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-3 h-3 bg-blue-400 rounded-full animate-bounce"
                style={{ animationDelay: `${i * 0.1}s` }}
              />
            ))}
          </div>
        </div>
        
        {/* Footer */}
        <div className="mt-12 text-sm text-blue-200">
          Built with Rust + React + Electron
        </div>
      </div>
    </div>
  );
};

export default LoadingScreen;
