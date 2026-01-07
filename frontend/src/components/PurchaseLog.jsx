import React, { useState, useEffect } from 'react';
import api from '../api';
import { Search, UserPlus, Shield, AlertCircle, CheckCircle } from 'lucide-react';

function PurchaseLog() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showLogForm, setShowLogForm] = useState(false);
  const [users, setUsers] = useState([]);
  const [shops, setShops] = useState([]);
  const [formData, setFormData] = useState({
    user_id: '',
    shop_id: '',
    alcohol_type: 'Beer',
    brand: '',
    quantity_ml: '',
    abv_percentage: '',
    amount_paid: '',
    payment_method: 'Cash',
  });

  useEffect(() => {
    fetchTransactions();
    fetchUsers();
    fetchShops();
  }, []);

  const fetchTransactions = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/transactions/recent?limit=100');
      setTransactions(response.data.transactions);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await api.get('/api/users/');
      setUsers(response.data.users);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchShops = async () => {
    try {
      // We don't have a shops endpoint yet, so we'll use mock data
      setShops([
        { shop_id: 1, shop_name: 'TASMAC Chennai Shop 1' },
        { shop_id: 2, shop_name: 'TASMAC Coimbatore Shop 1' },
        { shop_id: 3, shop_name: 'TASMAC Madurai Shop 1' },
      ]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogPurchase = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/transactions/log', {
        user_id: parseInt(formData.user_id),
        shop_id: parseInt(formData.shop_id),
        alcohol_type: formData.alcohol_type,
        brand: formData.brand,
        quantity_ml: parseInt(formData.quantity_ml),
        abv_percentage: parseFloat(formData.abv_percentage),
        amount_paid: parseFloat(formData.amount_paid),
        payment_method: formData.payment_method,
      });
      setShowLogForm(false);
      setFormData({
        user_id: '',
        shop_id: '',
        alcohol_type: 'Beer',
        brand: '',
        quantity_ml: '',
        abv_percentage: '',
        amount_paid: '',
        payment_method: 'Cash',
      });
      fetchTransactions();
      alert('Purchase logged successfully!');
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to log purchase');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Purchase Log</h2>
        <button
          onClick={() => setShowLogForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600"
        >
          <ShoppingCart className="w-4 h-4" />
          Log New Purchase
        </button>
      </div>

      {/* Log Purchase Form */}
      {showLogForm && (
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">Log New Purchase</h3>
          <form onSubmit={handleLogPurchase} className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                User *
              </label>
              <select
                required
                value={formData.user_id}
                onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
              >
                <option value="">Select User</option>
                {users.map((user) => (
                  <option key={user.user_id} value={user.user_id}>
                    {user.name} ({user.aadhaar_mock})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Shop *
              </label>
              <select
                required
                value={formData.shop_id}
                onChange={(e) => setFormData({ ...formData, shop_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
              >
                <option value="">Select Shop</option>
                {shops.map((shop) => (
                  <option key={shop.shop_id} value={shop.shop_id}>
                    {shop.shop_name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Alcohol Type *
              </label>
              <select
                required
                value={formData.alcohol_type}
                onChange={(e) => setFormData({ ...formData, alcohol_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
              >
                <option>Beer</option>
                <option>Whiskey</option>
                <option>Rum</option>
                <option>Vodka</option>
                <option>Brandy</option>
                <option>Wine</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Brand *
              </label>
              <input
                type="text"
                required
                value={formData.brand}
                onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quantity (ml) *
              </label>
              <input
                type="number"
                required
                value={formData.quantity_ml}
                onChange={(e) => setFormData({ ...formData, quantity_ml: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                placeholder="e.g., 750"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                ABV % *
              </label>
              <input
                type="number"
                step="0.1"
                required
                value={formData.abv_percentage}
                onChange={(e) => setFormData({ ...formData, abv_percentage: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                placeholder="e.g., 5.0"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Amount Paid (₹) *
              </label>
              <input
                type="number"
                step="0.01"
                required
                value={formData.amount_paid}
                onChange={(e) => setFormData({ ...formData, amount_paid: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
                placeholder="e.g., 150.00"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Payment Method *
              </label>
              <select
                required
                value={formData.payment_method}
                onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary"
              >
                <option>Cash</option>
                <option>Card</option>
                <option>UPI</option>
              </select>
            </div>
            <div className="col-span-2 flex gap-3">
              <button
                type="submit"
                className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600"
              >
                Log Purchase
              </button>
              <button
                type="button"
                onClick={() => setShowLogForm(false)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Transactions Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date & Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  User ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Units
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Payment
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {transactions.map((transaction) => (
                <tr key={transaction.transaction_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      {formatDate(transaction.transaction_date)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    #{transaction.user_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <Wine className="w-4 h-4 text-primary" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {transaction.brand || 'N/A'}
                        </div>
                        <div className="text-xs text-gray-500">
                          {transaction.alcohol_type}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {transaction.quantity_ml} ml
                    <div className="text-xs text-gray-500">
                      {transaction.abv_percentage}% ABV
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {transaction.units?.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center gap-1">
                      <DollarSign className="w-4 h-4 text-green-600" />
                      ₹{transaction.amount_paid}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {transaction.payment_method}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="text-sm text-gray-500">
        Showing {transactions.length} recent transactions
      </div>
    </div>
  );
}

export default PurchaseLog;
