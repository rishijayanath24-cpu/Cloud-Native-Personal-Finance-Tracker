import React, { useState, useEffect } from 'react';
import api from '../services/api';
import toast from 'react-hot-toast';
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline';

const CATEGORIES = ['Food', 'Housing', 'Transportation', 'Healthcare', 'Entertainment', 'Education', 'Shopping', 'Utilities', 'Other'];

function BudgetCard({ budget, onDelete }) {
  const usage = budget.usage_percentage || 0;
  const color = usage >= 100 ? 'bg-red-500' : usage >= 80 ? 'bg-yellow-500' : 'bg-green-500';

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold">{budget.name}</h3>
          <p className="text-sm text-gray-500">{budget.category} · {budget.period}</p>
        </div>
        <button onClick={() => onDelete(budget.id)} className="text-red-400 hover:text-red-600">
          <TrashIcon className="h-4 w-4" />
        </button>
      </div>
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">${budget.spent_amount?.toFixed(2)} spent</span>
          <span className="font-medium">${budget.limit_amount?.toFixed(2)} limit</span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div className={`h-full ${color} transition-all`} style={{ width: `${Math.min(usage, 100)}%` }} />
        </div>
        <p className={`text-xs font-medium ${usage >= 100 ? 'text-red-600' : usage >= 80 ? 'text-yellow-600' : 'text-green-600'}`}>
          {usage.toFixed(1)}% used
          {usage >= budget.alert_threshold && usage < 100 && ' · Alert threshold reached'}
          {usage >= 100 && ' · Budget exceeded!'}
        </p>
      </div>
    </div>
  );
}

function BudgetModal({ onClose, onSave }) {
  const [form, setForm] = useState({ name: '', category: 'Food', limit_amount: '', period: 'monthly', alert_threshold: 80 });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/api/budgets/', { ...form, limit_amount: parseFloat(form.limit_amount), alert_threshold: parseFloat(form.alert_threshold) });
      toast.success('Budget created!');
      onSave();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create budget');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="card w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">Create Budget</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Budget Name</label>
            <input type="text" className="input" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <select className="input" value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
              {CATEGORIES.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium mb-1">Limit Amount ($)</label>
              <input type="number" step="0.01" min="0" className="input" value={form.limit_amount} onChange={e => setForm({...form, limit_amount: e.target.value})} required />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Period</label>
              <select className="input" value={form.period} onChange={e => setForm({...form, period: e.target.value})}>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Alert Threshold (%)</label>
            <input type="number" min="0" max="100" className="input" value={form.alert_threshold} onChange={e => setForm({...form, alert_threshold: e.target.value})} />
          </div>
          <div className="flex gap-3">
            <button type="button" className="btn-secondary flex-1" onClick={onClose}>Cancel</button>
            <button type="submit" disabled={loading} className="btn-primary flex-1">{loading ? 'Creating...' : 'Create'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const fetchBudgets = () => {
    setLoading(true);
    api.get('/api/budgets/')
      .then(res => setBudgets(res.data))
      .catch(() => toast.error('Failed to load budgets'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchBudgets(); }, []);

  const handleDelete = async (id) => {
    if (!confirm('Delete this budget?')) return;
    try {
      await api.delete(`/api/budgets/${id}`);
      toast.success('Budget deleted');
      fetchBudgets();
    } catch {
      toast.error('Failed to delete');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Budgets</h1>
          <p className="text-gray-500">Manage your spending goals</p>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={() => setShowModal(true)}>
          <PlusIcon className="h-4 w-4" /> Add Budget
        </button>
      </div>
      {loading ? (
        <div className="flex items-center justify-center h-32"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div></div>
      ) : budgets.length === 0 ? (
        <div className="card text-center py-12 text-gray-400">No budgets yet. Create your first budget to start tracking!</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {budgets.map(b => <BudgetCard key={b.id} budget={b} onDelete={handleDelete} />)}
        </div>
      )}
      {showModal && <BudgetModal onClose={() => setShowModal(false)} onSave={() => { setShowModal(false); fetchBudgets(); }} />}
    </div>
  );
}
