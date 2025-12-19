'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getAccounts } from '../../lib/api';
import type { Account } from '../../lib/types';
import { validateAmount } from '../../lib/utils';
import styles from './page.module.css';



export default function NewPaymentPage() {

  // Accounts lists from API
  const [debtorAccounts, setDebtorAccounts] = useState<Account[]>([]);
  const [creditorAccounts, setCreditorAccounts] = useState<Account[]>([]);
  
  // Form fields
  const [debtorAccountId, setDebtorAccountId] = useState('');
  const [creditorAccountId, setCreditorAccountId] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  
  // Validation errors
  const [errors, setErrors] = useState<{
    debtorAccountId?: string;
    creditorAccountId?: string;
    amount?: string;
  }>({});
  
  // Loading state
  const [loading, setLoading] = useState(true);
  
  // Router for navigation
  const router = useRouter();

  
  /**
   * Fetch accounts on component mount
   */
  useEffect(() => {
    async function fetchAccounts() {
      try {
        const accounts = await getAccounts();
        
        // Separate debtor and creditor accounts
        const debtors = accounts.filter(acc => acc.account_type === 'debtor');
        const creditors = accounts.filter(acc => acc.account_type === 'creditor');
        
        setDebtorAccounts(debtors);
        setCreditorAccounts(creditors);
        
        // Pre-select first account if available
        if (debtors.length > 0) {
          setDebtorAccountId(debtors[0].account_id);
        }
        
      } catch (error) {
        console.error('Failed to fetch accounts:', error);
        alert('Failed to load accounts. Please refresh the page.');
      } finally {
        setLoading(false);
      }
    }
    
    fetchAccounts();
  }, []);

  
  /**
   * Validate entire form
   * Returns true if valid, false otherwise
   */
  const validateForm = (): boolean => {
    const newErrors: typeof errors = {};
    
    // Validate debtor account
    if (!debtorAccountId) {
      newErrors.debtorAccountId = 'Please select a payment account';
    }
    
    // Validate creditor account
    if (!creditorAccountId) {
      newErrors.creditorAccountId = 'Please select a recipient account';
    }
    
    // Check if accounts are the same
    if (debtorAccountId && creditorAccountId && debtorAccountId === creditorAccountId) {
      newErrors.creditorAccountId = 'Recipient must be different from payment account';
    }
    
    // Validate amount
    const amountError = validateAmount(amount);
    if (amountError) {
      newErrors.amount = amountError;
    }
    
    // Check sufficient balance
    if (!amountError && debtorAccountId) {
      const debtorAccount = debtorAccounts.find(acc => acc.account_id === debtorAccountId);
      const amountNum = parseFloat(amount);
      
      if (debtorAccount && amountNum > debtorAccount.balance) {
        newErrors.amount = `Insufficient balance. Available: $${debtorAccount.balance.toLocaleString()}`;
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  
  /**
   * Handle form submission
   */
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();  // Prevent default form submission
    
    // Validate form
    if (!validateForm()) {
      return;
    }
    
    // Get account names for display
    const debtorAccount = debtorAccounts.find(acc => acc.account_id === debtorAccountId);
    const creditorAccount = creditorAccounts.find(acc => acc.account_id === creditorAccountId);
    
    // Prepare payment data
    const paymentData = {
      debtor_account_id: debtorAccountId,
      creditor_account_id: creditorAccountId,
      transaction_amount: parseFloat(amount),
      description: description.trim() || undefined,
      // Store names for preview display
      debtor_name: debtorAccount?.account_name,
      creditor_name: creditorAccount?.account_name,
      debtor_balance: debtorAccount?.balance,
    };
    
    // Store in sessionStorage
    sessionStorage.setItem('pendingPayment', JSON.stringify(paymentData));
    
    // Navigate to preview page
    router.push('/payments/preview');
  };
  
  /**
   * Handle cancel button
   */
  const handleCancel = () => {
    router.push('/payments');
  };
  
  /**
   * Handle amount change with real-time validation
   */
  const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setAmount(value);
    
    // Clear error when user starts typing
    if (errors.amount) {
      setErrors({ ...errors, amount: undefined });
    }
  };
  
  /**
   * Handle amount blur (when user leaves field)
   */
  const handleAmountBlur = () => {
    if (amount) {
      const error = validateAmount(amount);
      if (error) {
        setErrors({ ...errors, amount: error });
      }
    }
  };

  
  /**
   * Get selected debtor account object
   */
  const selectedDebtorAccount = debtorAccounts.find(
    acc => acc.account_id === debtorAccountId
  );

  
  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className="spinner-lg"></div>
          <p>Loading accounts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        {/* Header */}
        <div className={styles.header}>
          <h1 className={styles.title}>💳 Create New Payment</h1>
          <p className={styles.subtitle}>
            Enter payment details to initiate a transaction
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className={styles.form}>
          {/* From Account Field */}
          <div className="form-group">
            <label htmlFor="debtor-account" className="form-label form-label-required">
              From Account
            </label>
            <select
              id="debtor-account"
              value={debtorAccountId}
              onChange={(e) => setDebtorAccountId(e.target.value)}
              className={`form-select ${errors.debtorAccountId ? 'form-select-error' : ''}`}
              required
            >
              <option value="">Select payment account</option>
              {debtorAccounts.map((account) => (
                <option key={account.account_id} value={account.account_id}>
                  {account.account_name} (Balance: ${account.balance.toLocaleString()})
                </option>
              ))}
            </select>
            {errors.debtorAccountId && (
              <span className="form-error">{errors.debtorAccountId}</span>
            )}
            {selectedDebtorAccount && (
              <span className="form-help">
                Available balance: ${selectedDebtorAccount.balance.toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </span>
            )}
          </div>

          {/* To Account Field */}
          <div className="form-group">
            <label htmlFor="creditor-account" className="form-label form-label-required">
              To Account
            </label>
            <select
              id="creditor-account"
              value={creditorAccountId}
              onChange={(e) => setCreditorAccountId(e.target.value)}
              className={`form-select ${errors.creditorAccountId ? 'form-select-error' : ''}`}
              required
            >
              <option value="">Select recipient account</option>
              {creditorAccounts.map((account) => (
                <option key={account.account_id} value={account.account_id}>
                  {account.account_name}
                </option>
              ))}
            </select>
            {errors.creditorAccountId && (
              <span className="form-error">{errors.creditorAccountId}</span>
            )}
          </div>

          {/* Amount Field */}
          <div className="form-group">
            <label htmlFor="amount" className="form-label form-label-required">
              Amount (USD)
            </label>
            <input
              id="amount"
              type="number"
              step="0.01"
              min="0"
              value={amount}
              onChange={handleAmountChange}
              onBlur={handleAmountBlur}
              placeholder="0.00"
              className={`form-input ${errors.amount ? 'form-input-error' : ''}`}
              required
            />
            {errors.amount && (
              <span className="form-error">{errors.amount}</span>
            )}
            <span className="form-help">
              Enter the amount in US Dollars (max 2 decimal places)
            </span>
          </div>

          {/* Description Field */}
          <div className="form-group">
            <label htmlFor="description" className="form-label">
              Description (Optional)
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="e.g., Purchase office supplies"
              className="form-textarea"
              rows={3}
              maxLength={500}
            />
            <span className="form-help">
              {description.length}/500 characters
            </span>
          </div>

          {/* Action Buttons */}
          <div className={styles.actions}>
            <button
              type="button"
              onClick={handleCancel}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
            >
              Next: Preview →
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}