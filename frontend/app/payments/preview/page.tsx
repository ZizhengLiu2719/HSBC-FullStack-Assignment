'use client';

import { createPayment } from '@/app/lib/api';
import { formatCurrency } from '@/app/lib/utils';
import { useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import styles from './page.module.css';

/**
 * Payment Preview Page
 * Route: /payments/preview
 * 
 * Purpose:
 * - Display payment details for final review
 * - Give user chance to edit before submission
 * - Confirm payment and submit to backend
 * 
 * Why this design?
 * - Assignment requirement: "Review and confirm payment details before execution"
 * - Assignment requirement: "No irreversible actions without explicit confirmation"
 * - Clear visual hierarchy shows what's being paid
 * - Warning message emphasizes importance of confirmation
 * 
 * Data Flow:
 * 1. Read payment data from sessionStorage
 * 2. Display for review
 * 3. User confirms → POST to API
 * 4. Navigate to status page with transaction ID
 */

/**
 * Interface for pending payment data stored in sessionStorage
 */
interface PendingPaymentData {
  debtor_account_id: string;
  creditor_account_id: string;
  transaction_amount: number;
  description?: string;
  debtor_name?: string;
  creditor_name?: string;
  debtor_balance?: number;
}

export default function PreviewPage() {
  // ========================================
  // State Management with Lazy Initialization
  // ========================================
  
  const router = useRouter();
  const redirectedRef = useRef(false);
  
  // Lazy initialization: read from sessionStorage only once
  const [paymentData] = useState<PendingPaymentData | null>(() => {
    // This function only runs once during initial render
    if (typeof window === 'undefined') return null;
    
    const stored = sessionStorage.getItem('pendingPayment');
    if (!stored) return null;
    
    try {
      return JSON.parse(stored) as PendingPaymentData;
    } catch (err) {
      console.error('Failed to parse payment data:', err);
      return null;
    }
  });
  
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ========================================
  // Handle Redirect if No Payment Data
  // ========================================
  
  useEffect(() => {
    if (!paymentData && !redirectedRef.current) {
      redirectedRef.current = true;
      router.push('/payments/new');
    }
  }, [paymentData, router]);

  // ========================================
  // Event Handlers
  // ========================================
  
  /**
   * Handle back button - return to edit
   */
  const handleBack = () => {
    router.back();  // Go to previous page (should be /payments/new)
  };
  
  /**
   * Handle confirm - submit payment to API
   */
  const handleConfirm = async () => {
    if (!paymentData) return;
    
    try {
      setSubmitting(true);
      setError(null);
      
      // Prepare API request data
      const requestData = {
        debtor_account_id: paymentData.debtor_account_id,
        creditor_account_id: paymentData.creditor_account_id,
        transaction_amount: paymentData.transaction_amount,
        description: paymentData.description,
      };
      
      // Submit to API
      const response = await createPayment(requestData);
      
      // Clear sessionStorage
      sessionStorage.removeItem('pendingPayment');
      
      // Navigate to status page
      router.push(`/payments/${response.transaction_id}`);
      
    } catch (err) {
      console.error('Failed to create payment:', err);
      const error = err as { error?: { code?: string; message?: string } };
      
      // Display user-friendly error message
      if (error.error?.code === 'INSUFFICIENT_BALANCE') {
        setError('Insufficient balance. Please go back and select a different account or amount.');
      } else if (error.error?.message) {
        setError(error.error.message);
      } else {
        setError('Failed to create payment. Please try again.');
      }
      
      setSubmitting(false);
    }
  };

  // ========================================
  // Render
  // ========================================
  
  // Loading state
  if (!paymentData) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className="spinner-lg"></div>
          <p>Loading payment details...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        {/* Header */}
        <div className={styles.header}>
          <h1 className={styles.title}>✓ Confirm Payment Details</h1>
          <p className={styles.subtitle}>
            Please review the information below carefully
          </p>
        </div>

        {/* Payment Details */}
        <div className={styles.details}>
          {/* From Account */}
          <div className={styles.section}>
            <div className={styles.sectionHeader}>
              <span className={styles.icon}>💼</span>
              <h2 className={styles.sectionTitle}>From</h2>
            </div>
            <div className={styles.sectionContent}>
              <div className={styles.accountName}>
                {paymentData.debtor_name || paymentData.debtor_account_id}
              </div>
              <div className={styles.accountInfo}>
                Account ID: {paymentData.debtor_account_id}
              </div>
              {paymentData.debtor_balance !== undefined && (
                <div className={styles.accountBalance}>
                  Current Balance: {formatCurrency(paymentData.debtor_balance)}
                </div>
              )}
            </div>
          </div>

          {/* Arrow */}
          <div className={styles.arrow}>
            <span>↓</span>
          </div>

          {/* To Account */}
          <div className={styles.section}>
            <div className={styles.sectionHeader}>
              <span className={styles.icon}>🏢</span>
              <h2 className={styles.sectionTitle}>To</h2>
            </div>
            <div className={styles.sectionContent}>
              <div className={styles.accountName}>
                {paymentData.creditor_name || paymentData.creditor_account_id}
              </div>
              <div className={styles.accountInfo}>
                Account ID: {paymentData.creditor_account_id}
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className={styles.divider}></div>

          {/* Amount */}
          <div className={styles.amountSection}>
            <div className={styles.amountLabel}>
              💰 Payment Amount
            </div>
            <div className={styles.amountValue}>
              {formatCurrency(paymentData.transaction_amount)} USD
            </div>
          </div>

          {/* Description */}
          {paymentData.description && (
            <div className={styles.descriptionSection}>
              <div className={styles.descriptionLabel}>
                📝 Description
              </div>
              <div className={styles.descriptionValue}>
                {paymentData.description}
              </div>
            </div>
          )}
        </div>

        {/* Warning Message */}
        <div className={styles.warning}>
          <span className={styles.warningIcon}>⚠️</span>
          <div className={styles.warningText}>
            <strong>Please review carefully.</strong>
            <br />
            Once confirmed, the payment will be submitted for processing.
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className={styles.error}>
            <span className={styles.errorIcon}>❌</span>
            <div className={styles.errorText}>{error}</div>
          </div>
        )}

        {/* Action Buttons */}
        <div className={styles.actions}>
          <button
            type="button"
            onClick={handleBack}
            disabled={submitting}
            className="btn btn-secondary"
          >
            ← Back to Edit
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            disabled={submitting}
            className="btn btn-primary btn-lg"
          >
            {submitting ? (
              <>
                <span className="spinner"></span>
                Submitting...
              </>
            ) : (
              '✓ Confirm & Submit Payment'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}