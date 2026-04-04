import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../services/api';
import toast from 'react-hot-toast';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function StatCard({ title, value, subtitle, color = 'primary' }) {
  const colorMap = { primary: 'text-primary-600', green: 'text-green-600', red: 'text-red-600', yellow: 'text-yellow-600' };
  return (
    <div className="card">
      <p className="text-sm text-gray-500 mb-1">{title}</p>
      <p className={`text-2xl font-bold ${colorMap[color]}`}>{value}</p>
      {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/api/transactions/summary')
      .then(res => setSummary(res.data))
      .catch(() => toast.error('Failed to load summary'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>;

  const categoryData = summary?.categories ? Object.entries(summary.categories).map(([name, value]) => ({ name, value: Math.abs(value) })) : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-gray-500">Your financial overview</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Income" value={`$${summary?.total_income?.toFixed(2) || '0.00'}`} color="green" />
        <StatCard title="Total Expenses" value={`$${summary?.total_expenses?.toFixed(2) || '0.00'}`} color="red" />
        <StatCard title="Net Balance" value={`$${summary?.net_balance?.toFixed(2) || '0.00'}`} color={summary?.net_balance >= 0 ? 'green' : 'red'} />
        <StatCard title="Transactions" value={summary?.transaction_count || 0} subtitle="Total recorded" />
      </div>
      {categoryData.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="font-semibold mb-4">Spending by Category</h3>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={categoryData} cx="50%" cy="50%" outerRadius={100} dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                  {categoryData.map((_, index) => <Cell key={index} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v) => `$${v.toFixed(2)}`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="card">
            <h3 className="font-semibold mb-4">Category Breakdown</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(v) => `$${v.toFixed(2)}`} />
                <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
      {categoryData.length === 0 && (
        <div className="card text-center py-12">
          <p className="text-gray-400 text-lg">No transactions yet</p>
          <p className="text-gray-300 text-sm mt-2">Start by adding your first transaction</p>
        </div>
      )}
    </div>
  );
}
