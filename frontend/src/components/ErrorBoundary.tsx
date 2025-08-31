import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('🚨 React Error Boundary Caught Error:', error);
    console.error('🚨 Error Info:', errorInfo);
    
    this.setState({
      error,
      errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div style={{
          padding: '50px',
          textAlign: 'center',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          border: '1px solid #f5c6cb',
          borderRadius: '8px',
          margin: '20px',
          fontFamily: 'Arial, sans-serif'
        }}>
          <h1>🚨 React App Crashed</h1>
          <p><strong>Error:</strong> {this.state.error?.message}</p>
          <details style={{ textAlign: 'left', marginTop: '20px' }}>
            <summary>Error Details</summary>
            <pre style={{ 
              backgroundColor: '#f8f9fa', 
              padding: '10px', 
              borderRadius: '4px',
              overflow: 'auto',
              fontSize: '12px'
            }}>
              {this.state.error?.stack}
            </pre>
            <pre style={{ 
              backgroundColor: '#f8f9fa', 
              padding: '10px', 
              borderRadius: '4px',
              overflow: 'auto',
              fontSize: '12px',
              marginTop: '10px'
            }}>
              {this.state.errorInfo?.componentStack}
            </pre>
          </details>
          <button 
            onClick={() => window.location.reload()} 
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Reload App
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
