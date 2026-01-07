import React, { useState, useEffect } from 'react';
import api from '../api';
import { Wine, ShieldAlert, CheckCircle, AlertTriangle } from 'lucide-react';

function ProductSelector({ user, onProductSelected, onCancel }) {
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [dailyLimit, setDailyLimit] = useState(null);
  const [loading, setLoading] = useState(true);

  const products = [
    { id: 1, name: 'Kingfisher Beer', type: 'Beer', ml: 650, abv: 5.0, price: 150, icon: '🍺' },
    { id: 2, name: 'Kingfisher Strong', type: 'Beer', ml: 650, abv: 8.0, price: 180, icon: '🍺' },
    { id: 3, name: 'Royal Stag', type: 'Whiskey', ml: 750, abv: 42.8, price: 1200, icon: '🥃' },
    { id: 4, name: 'McDowell No.1', type: 'Whiskey', ml: 375, abv: 42.8, price: 650, icon: '🥃' },
    { id: 5, name: 'Old Monk Rum', type: 'Rum', ml: 750, abv: 42.8, price: 600, icon: '🍹' },
    { id: 6, name: 'Magic Moments Vodka', type: 'Vodka', ml: 750, abv: 40.0, price: 800, icon: '🍸' },
  ];

  useEffect(() => {
    checkDailyLimit();
  }, []);

  const checkDailyLimit = async () => {
    try {
      // Get user's transactions today
      const today = new Date().toISOString().split('T')[0];
      const response = await api.get(`/api/transactions/user/${user.user_id}`, {
        params: { start_date: today }
      });
      
      const todayTransactions = response.data.transactions;
      const unitsToday = todayTransactions.reduce((sum, t) => sum + (t.units || 0), 0);
      
      setDailyLimit({
        used: unitsToday,
        remaining: Math.max(0, 5 - unitsToday),
        limit: 5
      });
    } catch (err) {
      // If no transactions, assume 0 units used
      setDailyLimit({ used: 0, remaining: 5, limit: 5 });
    } finally {
      setLoading(false);
    }
  };

  const calculateUnits = (product) => {
    return (product.ml * product.abv) / 1000;
  };

  const canPurchase = (product) => {
    if (!dailyLimit) return false;
    const units = calculateUnits(product);
    return dailyLimit.remaining >= units;
  };

  const handleProductClick = (product) => {
    setSelectedProduct(product);
  };

  const handleConfirm = async () => {
    if (!selectedProduct) return;

    const units = calculateUnits(selectedProduct);

    if (!canPurchase(selectedProduct)) {
      alert('Daily limit exceeded! Cannot complete purchase.');
      return;
    }

    try {
      // Log the purchase
      const response = await api.post('/api/transactions/log', {
        user_id: user.user_id,
        shop_id: 1,
        alcohol_type: selectedProduct.type,
        brand: selectedProduct.name,
        quantity_ml: selectedProduct.ml,
        abv_percentage: selectedProduct.abv,
        units: units,
        amount_paid: selectedProduct.price,
        payment_method: 'Cash'
      });

      onProductSelected({
        ...selectedProduct,
        units: units,
        transaction: response.data
      });
    } catch (err) {
      if (err.response?.data?.error) {
        alert(err.response.data.error);
      } else {
        alert('Failed to process purchase');
      }
    }
  };

  const getRiskBadge = () => {
    const colors = {
      Green: 'bg-green-100 text-green-800 border-green-300',
      Yellow: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      Red: 'bg-red-100 text-red-800 border-red-300'
    };
    
    const icons = {
      Green: <CheckCircle className="w-4 h-4" />,
      Yellow: <AlertTriangle className="w-4 h-4" />,
      Red: <ShieldAlert className="w-4 h-4" />
    };

    return (
      <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border-2 ${colors[user.risk_level]}`}>
        {icons[user.risk_level]}
        <span className="font-semibold">{user.risk_level} Risk Level</span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div>
      {/* User Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex justify-between items-center mb-3">
          <div>
            <p className="text-sm text-gray-600">Welcome,</p>
            <p className="text-xl font-bold text-gray-900">{user.name}</p>
          </div>
          {getRiskBadge()}
        </div>
        
        {/* Daily Limit Display */}
        <div className="mt-4 p-3 bg-white rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Daily Limit Status</span>
            <span className="text-lg font-bold text-primary">
              {dailyLimit.remaining.toFixed(1)} / {dailyLimit.limit} units
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${
                dailyLimit.remaining > 2 ? 'bg-green-500' :
                dailyLimit.remaining > 1 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${(dailyLimit.remaining / dailyLimit.limit) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Product Selection */}
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Product</h3>
      
      <div className="grid grid-cols-2 gap-4 mb-6">
        {products.map((product) => {
          const units = calculateUnits(product);
          const allowed = canPurchase(product);
          
          return (
            <button
              key={product.id}
              onClick={() => handleProductClick(product)}
              disabled={!allowed}
              className={`p-4 rounded-lg border-2 text-left transition-all ${
                selectedProduct?.id === product.id
                  ? 'border-primary bg-blue-50'
                  : allowed
                  ? 'border-gray-200 hover:border-gray-300 bg-white'
                  : 'border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed'
              }`}
            >
              <div className="text-3xl mb-2">{product.icon}</div>
              <div className="font-semibold text-gray-900">{product.name}</div>
              <div className="text-sm text-gray-600">{product.ml}ml • {product.abv}%</div>
              <div className="text-lg font-bold text-primary mt-2">₹{product.price}</div>
              <div className="text-xs text-gray-500 mt-1">
                {units.toFixed(1)} units
                {!allowed && <span className="text-red-600 font-medium"> - Exceeds limit</span>}
              </div>
            </button>
          );
        })}
      </div>

      {/* Warning for Red Users */}
      {user.risk_level === 'Red' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex gap-3">
            <ShieldAlert className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-900">High Risk Account</p>
              <p className="text-sm text-red-700 mt-1">
                Your purchase will require manager approval due to your risk status.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={onCancel}
          className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
        >
          Cancel
        </button>
        <button
          onClick={handleConfirm}
          disabled={!selectedProduct}
          className="flex-1 px-6 py-3 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {user.risk_level === 'Red' ? 'Request Approval' : 'Confirm Purchase'}
        </button>
      </div>
    </div>
  );
}

export default ProductSelector;
