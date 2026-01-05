import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, ShoppingCart, AlertTriangle, Activity, TrendingUp } from 'lucide-react';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/analytics/dashboard');
      setStats(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch dashboard statistics');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button
          onClick={fetchDashboardStats}
          className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!stats) return null;

  const statCards = [
    {
      title: 'Total Users',
      value: stats.users.total,
      subtitle: `${stats.users.blocked} blocked`,
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      title: 'Total Transactions',
      value: stats.transactions.total,
      subtitle: `${stats.transactions.last_30_days} in last 30 days`,
      icon: ShoppingCart,
      color: 'bg-green-500',
    },
    {
      title: 'Total Incidents',
      value: stats.incidents.total,
      subtitle: `${stats.incidents.last_30_days} recent`,
      icon: AlertTriangle,
      color: 'bg-red-500',
    },
    {
      title: 'Active Alerts',
      value: stats.alerts.active,
      subtitle: 'Requiring attention',
      icon: Activity,
      color: 'bg-yellow-500',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">System Overview</h2>
        <button
          onClick={fetchDashboardStats}
          className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className="bg-white rounded-lg shadow-sm p-6 border border-gray-200"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {stat.value.toLocaleString()}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">{stat.subtitle}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Risk Distribution */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Risk Level Distribution
        </h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="text-3xl font-bold text-green-600">
              {stats.users.risk_distribution.Green || 0}
            </div>
            <div className="text-sm text-gray-600 mt-1">Green (Low Risk)</div>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <div className="text-3xl font-bold text-yellow-600">
              {stats.users.risk_distribution.Yellow || 0}
            </div>
            <div className="text-sm text-gray-600 mt-1">Yellow (Medium Risk)</div>
          </div>
          <div className="text-center p-4 bg-red-50 rounded-lg border border-red-200">
            <div className="text-3xl font-bold text-red-600">
              {stats.users.risk_distribution.Red || 0}
            </div>
            <div className="text-sm text-gray-600 mt-1">Red (High Risk)</div>
          </div>
        </div>
      </div>

      {/* Consumption Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold text-gray-900">
              Alcohol Consumption
            </h3>
          </div>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-gray-600">Total Units Consumed</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.transactions.total_units_consumed.toLocaleString(undefined, {
                  maximumFractionDigits: 0,
                })}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Average per Transaction</p>
              <p className="text-xl font-semibold text-gray-700">
                {(
                  stats.transactions.total_units_consumed / stats.transactions.total
                ).toFixed(2)}{' '}
                units
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Active Pattern Flags</span>
              <span className="text-lg font-semibold text-gray-900">
                {stats.patterns.active_flags}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Blocked Users</span>
              <span className="text-lg font-semibold text-red-600">
                {stats.users.blocked}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">System Health</span>
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                Operational
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;