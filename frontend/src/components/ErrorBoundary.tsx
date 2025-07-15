import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="max-w-md w-full space-y-8 p-8">
            <div className="text-center">
              <h1 className="text-2xl font-bold text-red-600 mb-4">
                Something went wrong
              </h1>
              <p className="text-gray-600 mb-4">
                An error occurred while rendering the application.
              </p>
              <div className="bg-red-50 border border-red-200 rounded-md p-4 text-left">
                <p className="text-sm font-medium text-red-800 mb-2">Error Details:</p>
                <p className="text-sm text-red-700 font-mono">
                  {this.state.error?.message}
                </p>
                <p className="text-sm text-red-700 font-mono mt-2">
                  {this.state.error?.stack}
                </p>
              </div>
              <button
                onClick={() => window.location.reload()}
                className="mt-4 btn-primary"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 