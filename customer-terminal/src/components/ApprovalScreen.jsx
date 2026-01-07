import React, { useState, useEffect } from 'react';
import { Clock, ShieldAlert } from 'lucide-react';
import { ShoppingCart, Calendar, Wine, DollarSign } from "lucide-react";

function ApprovalScreen({ user, product, onApproved, onDenied, socket }) {
  const [status, setStatus] = useState('waiting');
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    // Listen for approval/denial from organization dashboard
    if (socket) {
      socket.on('approval_response', (data) => {
        if (data.approved) {
          setStatus('approved');
          setTimeout(() => onApproved(), 2000);
        } else {
          setStatus('denied');
          setTimeout(() => onDenied(), 3000);
        }
      });
    }

    // Timer
    const timer = setInterval(() => {
      setElapsed(prev => prev + 1);
    }, 1000);

    // Auto-timeout after 60 seconds
    const timeout = setTimeout(() => {
      if (status === 'waiting') {
        setStatus('timeout');
        setTimeout(() => onDenied(), 3000);
      }
    }, 60000);

    return () => {
      clearInterval(timer);
      clearTimeout(timeout);
      if (socket) {
        socket.off('approval_response');
      }
    };
  }, [socket, status, onApproved, onDenied]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="text-center py-8">
      {status === 'waiting' && (
        <>
          <div className="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
            <ShieldAlert className="w-12 h-12 text-yellow-600" />
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Manager Approval Required
          </h2>
          <p className="text-gray-600 mb-8">
            Due to your high-risk status, this purchase requires manager authorization
          </p>

          <div className="bg-gray-50 rounded-lg p-6 mb-6 max-w-md mx-auto">
            <div className="space-y-3 text-left">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Customer:</span>
                <span className="font-semibold">{user.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Risk Level:</span>
                <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm font-medium">
                  {user.risk_level}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Product:</span>
                <span className="font-semibold">{product.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Units:</span>
                <span className="font-semibold">{product.units.toFixed(1)}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-center gap-2 text-gray-500">
            <Clock className="w-5 h-5" />
            <span>Waiting for approval... {formatTime(elapsed)}</span>
          </div>

          <div className="mt-8">
            <div className="flex justify-center gap-2 mb-2">
              <div className="w-3 h-3 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <p className="text-sm text-gray-500">Please wait at the counter</p>
          </div>
        </>
      )}

      {status === 'approved' && (
        <>
          <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-5xl">✅</span>
          </div>
          <h2 className="text-3xl font-bold text-green-600 mb-4">
            Purchase Approved!
          </h2>
          <p className="text-lg text-gray-700">
            Manager has authorized your purchase
          </p>
        </>
      )}

      {status === 'denied' && (
        <>
          <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-5xl">❌</span>
          </div>
          <h2 className="text-3xl font-bold text-red-600 mb-4">
            Purchase Denied
          </h2>
          <p className="text-lg text-gray-700 mb-2">
            Manager has declined this purchase
          </p>
          <p className="text-sm text-gray-500">
            Please contact TASMAC administration for more information
          </p>
        </>
      )}

      {status === 'timeout' && (
        <>
          <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-5xl">⏱️</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-600 mb-4">
            Request Timeout
          </h2>
          <p className="text-lg text-gray-700">
            No response from manager. Please try again.
          </p>
        </>
      )}
    </div>
  );
}

export default ApprovalScreen;
