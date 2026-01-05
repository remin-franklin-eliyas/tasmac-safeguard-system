import React, { useEffect } from 'react';
import { CheckCircle, Receipt } from 'lucide-react';

function TransactionComplete({ transaction, onReset }) {
  useEffect(() => {
    // Auto-reset after 10 seconds
    const timer = setTimeout(() => {
      onReset();
    }, 10000);

    return () => clearTimeout(timer);
  }, [onReset]);

  return (
    <div className="text-center py-8">
      <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6 animate-bounce">
        <CheckCircle className="w-16 h-16 text-green-600" />
      </div>

      <h2 className="text-3xl font-bold text-green-600 mb-2">
        Purchase Successful!
      </h2>
      <p className="text-lg text-gray-700 mb-8">
        Thank you for your purchase
      </p>

      {/* Receipt */}
      <div className="bg-white border-2 border-gray-300 rounded-lg p-6 max-w-md mx-auto mb-8 shadow-lg">
        <div className="flex items-center justify-center gap-2 mb-4 pb-4 border-b border-gray-200">
          <Receipt className="w-5 h-5 text-gray-600" />
          <span className="font-semibold text-gray-900">Transaction Receipt</span>
        </div>

        <div className="space-y-3 text-left">
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Customer:</span>
            <span className="font-semibold">{transaction.user.name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Product:</span>
            <span className="font-semibold">{transaction.product.name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Quantity:</span>
            <span className="font-semibold">{transaction.product.ml}ml</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Units:</span>
            <span className="font-semibold">{transaction.product.units.toFixed(2)}</span>
          </div>
          
          <div className="pt-3 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <span className="font-semibold text-gray-900">Total Amount:</span>
              <span className="text-2xl font-bold text-green-600">
                ₹{transaction.product.price}
              </span>
            </div>
          </div>

          <div className="pt-3 border-t border-gray-200">
            <div className="text-xs text-gray-500 text-center">
              {new Date(transaction.timestamp).toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      {/* Responsible Drinking Message */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 max-w-md mx-auto mb-6">
        <p className="text-sm text-yellow-800 font-medium">
          ⚠️ Please drink responsibly
        </p>
        <p className="text-xs text-yellow-700 mt-1">
          Do not drink and drive • Know your limits • Stay safe
        </p>
      </div>

      <button
        onClick={onReset}
        className="px-8 py-3 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors text-lg font-semibold"
      >
        Complete Transaction
      </button>

      <p className="text-sm text-gray-500 mt-4">
        Auto-returning to home in 10 seconds...
      </p>
    </div>
  );
}

export default TransactionComplete;