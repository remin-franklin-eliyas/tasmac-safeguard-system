import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import AadhaarScanner from './components/AadhaarScanner';
import ProductSelector from './components/ProductSelector';
import ApprovalScreen from './components/ApprovalScreen';
import TransactionComplete from './components/TransactionComplete';
import { Store, Wifi, WifiOff } from 'lucide-react';

function App() {
  const [step, setStep] = useState('scan'); // scan, select, approval, blocked, complete
  const [user, setUser] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [transaction, setTransaction] = useState(null);
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket
    const newSocket = io('https://tasmac-safeguard-system-production.up.railway.app');
    
    newSocket.on('connect', () => {
      console.log('Connected to server');
      setConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
      setConnected(false);
    });

    newSocket.on('connection_response', (data) => {
      console.log('Server response:', data);
    });

    setSocket(newSocket);

    return () => newSocket.close();
  }, []);

  const handleUserVerified = (userData) => {
    setUser(userData);
    
    if (userData.is_blocked) {
      setStep('blocked');
    } else {
      setStep('select');
    }
  };

  const handleProductSelected = (product) => {
    setSelectedProduct(product);
    
    // Check if high-risk user needs approval
    if (user.risk_level === 'Red') {
      setStep('approval');
      // Emit approval request via WebSocket
      if (socket) {
        socket.emit('approval_request', {
          user: user,
          product: product,
          timestamp: new Date().toISOString()
        });
      }
    } else {
      // Proceed with purchase
      completePurchase(product);
    }
  };

  const completePurchase = async (product) => {
    setTransaction({
      user: user,
      product: product,
      timestamp: new Date().toISOString(),
      status: 'approved'
    });
    setStep('complete');
  };

  const resetFlow = () => {
    setStep('scan');
    setUser(null);
    setSelectedProduct(null);
    setTransaction(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100">
      {/* Header */}
      <header className="bg-white shadow-md">
        <div className="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Store className="w-8 h-8 text-primary" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">TASMAC</h1>
              <p className="text-sm text-gray-500">Customer Purchase Terminal</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {connected ? (
              <span className="flex items-center gap-2 text-green-600 text-sm">
                <Wifi className="w-4 h-4" />
                Connected
              </span>
            ) : (
              <span className="flex items-center gap-2 text-red-600 text-sm">
                <WifiOff className="w-4 h-4" />
                Disconnected
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white rounded-2xl shadow-xl p-8 min-h-[600px]">
          {step === 'scan' && (
            <AadhaarScanner onUserVerified={handleUserVerified} />
          )}

          {step === 'select' && (
            <ProductSelector 
              user={user} 
              onProductSelected={handleProductSelected}
              onCancel={resetFlow}
            />
          )}

          {step === 'approval' && (
            <ApprovalScreen 
              user={user}
              product={selectedProduct}
              onApproved={() => completePurchase(selectedProduct)}
              onDenied={resetFlow}
              socket={socket}
            />
          )}

          {step === 'blocked' && (
            <div className="text-center py-12">
              <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-5xl">🚫</span>
              </div>
              <h2 className="text-3xl font-bold text-red-600 mb-4">
                Access Denied
              </h2>
              <p className="text-lg text-gray-700 mb-2">
                Your account has been blocked from purchasing alcohol.
              </p>
              <p className="text-sm text-gray-500 mb-8">
                Please contact TASMAC administration for more information.
              </p>
              <button
                onClick={resetFlow}
                className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Return to Home
              </button>
            </div>
          )}

          {step === 'complete' && (
            <TransactionComplete 
              transaction={transaction}
              onReset={resetFlow}
            />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-6 text-sm text-gray-500">
        <p>TASMAC SafeGuard System - Responsible Alcohol Sales</p>
      </footer>
    </div>
  );
}

export default App;
