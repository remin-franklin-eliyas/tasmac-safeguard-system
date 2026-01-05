import React, { useState } from 'react';
import axios from 'axios';
import { CreditCard, Loader } from 'lucide-react';

function AadhaarScanner({ onUserVerified }) {
  const [aadhaar, setAadhaar] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (aadhaar.length !== 12) {
      setError('Aadhaar must be exactly 12 digits');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Fetch all users and find by Aadhaar
      const response = await axios.get('/api/users/');
      const user = response.data.users.find(u => u.aadhaar_mock === aadhaar);

      if (!user) {
        setError('User not found. Please register at TASMAC office.');
        setLoading(false);
        return;
      }

      // Simulate card scan delay for realism
      setTimeout(() => {
        onUserVerified(user);
        setLoading(false);
      }, 1500);

    } catch (err) {
      setError('Failed to verify Aadhaar. Please try again.');
      setLoading(false);
    }
  };

  const quickSelect = (userId) => {
    // For demo: Quick select test users
    axios.get(`/api/users/${userId}`)
      .then(response => {
        onUserVerified(response.data);
      })
      .catch(err => {
        setError('Failed to load user');
      });
  };

  return (
    <div className="max-w-md mx-auto">
      <div className="text-center mb-8">
        <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <CreditCard className="w-10 h-10 text-primary" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Scan Aadhaar Card
        </h2>
        <p className="text-gray-600">
          Please scan your Aadhaar card to verify your identity
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Aadhaar Number
          </label>
          <input
            type="text"
            maxLength="12"
            value={aadhaar}
            onChange={(e) => setAadhaar(e.target.value.replace(/\D/g, ''))}
            placeholder="Enter 12-digit Aadhaar"
            className="w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            disabled={loading}
            autoFocus
          />
          <p className="text-xs text-gray-500 mt-1">
            {aadhaar.length}/12 digits
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={loading || aadhaar.length !== 12}
          className="w-full px-6 py-4 bg-primary text-white text-lg font-semibold rounded-lg hover:bg-blue-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              Verifying...
            </>
          ) : (
            'Verify Identity'
          )}
        </button>
      </form>

      {/* Demo Quick Select */}
      <div className="mt-8 pt-8 border-t border-gray-200">
        <p className="text-sm text-gray-600 mb-3 text-center">Demo: Quick Select User</p>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => quickSelect(1)}
            className="px-3 py-2 bg-green-100 text-green-700 rounded-lg text-sm hover:bg-green-200"
          >
            🟢 Green User
          </button>
          <button
            onClick={() => quickSelect(15)}
            className="px-3 py-2 bg-yellow-100 text-yellow-700 rounded-lg text-sm hover:bg-yellow-200"
          >
            🟡 Yellow User
          </button>
          <button
            onClick={() => quickSelect(30)}
            className="px-3 py-2 bg-red-100 text-red-700 rounded-lg text-sm hover:bg-red-200"
          >
            🔴 Red User
          </button>
          <button
            onClick={() => quickSelect(45)}
            className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200"
          >
            ⛔ Blocked User
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          Note: Block a user first in the organization dashboard
        </p>
      </div>
    </div>
  );
}

export default AadhaarScanner;