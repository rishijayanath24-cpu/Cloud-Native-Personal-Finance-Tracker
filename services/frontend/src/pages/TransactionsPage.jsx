import React, { useState, useEffect } from 'react';
import api from '../services/api';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline';

const CATEGORIES = ['Food', 'Housing', 'Transportation', 'Healthcare', 'Entertainment', 'Education', 'Shopping', 'Utilities', 'Salary', 'Freelance', 'Investment', 'Other'];

function TransactionModal({ onClose, onSave }) {
  const [form, setForm] = useState({ amount: '', transaction_type: 'expense', category: 'Food', description: '' });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/api/transactions/', { ...form, amount: parseFloat(form.amount) });
      toast.success('Transaction added!');
      onSave();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add transaction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="card w-full max-w-md">
        <h3 className="text-lg font-semibold mb-4">Add Transaction</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Type</label>
            <select className="input" value={form.transaction_type} onChange={e => setForm({...form, transaction_type: e.target.value})}>
              <option value="expense">Expense</option>
              <option value="income">Income</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Amount</label>
            <input type="number" step="0.01" min="0" className="input" value={form.amount} onChange={e => setForm({...form, amount: e.target.value})} required />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <select className="input" value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
              {CATEGORIES.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <input type="text" className="input" value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
          </div>
          <div className="flex gap-3">
            <button type="button" className="btn-secondary flex-1" onClick={onClose}>Cancel</button>
            <button type="submit" disabled={loading} className="btn-primary flex-1">{loading ? 'Saving...' : 'Save'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const fetchTransactions = () => {
    setLoading(true);
    api.get('/api/transactions/')
      .then(res => setTransactions(res.data))
      .catch(() => toast.error('Failed to load transactions'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchTransactions(); }, []);

  const handleDelete = async (id) => {
    if (!confirm('Delete this transaction?')) return;
    try {
      await api.delete(`/api/transactions/${id}`);
      toast.success('Transaction deleted');
      fetchTransactions();
    } catch {
      toast.error('Failed to delete');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Transactions</h1>
          <p className="text-gray-500">Track your income and expenses</p>
        </div>
        <button className="btn-primary flex items-center gap-2" onClick={() => setShowModal(true)}>
          <PlusIcon className="h-4 w-4" /> Add Transaction
        </button>
      </div>
      <div className="card overflow-hidden p-0">
        {loading ? (
          <div className="flex items-center justify-center h-32"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div></div>
        ) : transactions.length === 0 ? (
          <div className="text-center py-12 text-gray-400">No transactions yet</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                {['Date', 'Category', 'Description', 'Type', 'Amount', ''].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {transactions.map(t => (
                <tr key={t.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-500">{format(new Date(t.date), 'MMM dd, yyyy')}</td>
                  <td className="px-4 py-3 text-sm font-medium">{t.category}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{t.description || '-'}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${t.transaction_type === 'income' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      {t.transaction_type}
                    </span>
                  </td>
                  <td className={`px-4 py-3 text-sm font-bold ${t.transaction_type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                    {t.transaction_type === 'income' ? '+' : '-'}${t.amount.toFixed(2)}
                  </td>
                  <td className="px-4 py-3">
                    <button onClick={() => handleDelete(t.id)} className="text-red-400 hover:text-red-600">
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      {showModal && <TransactionModal onClose={() => setShowModal(false)} onSave={() => { setShowModal(false); fetchTransactions(); }} />}
    </div>
  );
}
