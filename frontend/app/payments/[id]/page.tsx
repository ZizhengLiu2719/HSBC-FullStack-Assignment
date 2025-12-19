'use client';

import StatusBadge from '@/app/components/StatusBadge/StatusBadge';
import { getPaymentById } from '@/app/lib/api';
import type { PaymentDetailResponse } from '@/app/lib/types';
import { formatCurrency, formatDateTime, getStatusText } from '@/app/lib/utils';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';
import styles from './page.module.css';



export default function PaymentDetailPage() {
  
  const params = useParams();
  const transactionId = params.id as string;


  
  const [payment, setPayment] = useState<PaymentDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pollingCount, setPollingCount] = useState(0);  // Track polling attempts

  
  /**
   * Fetch payment details from API
   * Wrapped in useCallback to avoid recreating on every render
   */
  const fetchPayment = useCallback(async () => {
    try {
      const data = await getPaymentById(transactionId);
      setPayment(data);
      setError(null);
      setPollingCount(prev => prev + 1);
    } catch (err) {
      console.error('Failed to fetch payment:', err);
      const error = err as { error?: { message?: string } };
      setError(error.error?.message || 'Failed to load payment details');
    } finally {
      setLoading(false);
    }
  }, [transactionId]);  // Only recreate if transactionId changes

  /**
   * Initial fetch on component mount
   */
  useEffect(() => {
    fetchPayment();
  }, [fetchPayment]);

  /**
   * Polling logic
   * Re-fetch every 2 seconds if status is pending or processing
   */
  useEffect(() => {
    // Don't poll if:
    // 1. Still loading
    // 2. Have error
    // 3. Payment is completed or failed
    if (loading || error || !payment) {
      return;
    }

    const status = payment.transaction_status;
    
    // Stop polling if payment is in final state
    if (status === 'completed' || status === 'failed') {
      return;
    }

    // Set up polling interval
    const intervalId = setInterval(() => {
      fetchPayment();
    }, 2000);  // Poll every 2 seconds

    // Cleanup: clear interval when component unmounts or dependencies change
    return () => clearInterval(intervalId);
  }, [loading, error, payment, fetchPayment]);

  
  /**
   * Check if status is in progress
   */
  const isInProgress = payment && 
    (payment.transaction_status === 'pending' || payment.transaction_status === 'processing');

  
  /**
   * Render loading state
   */
  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className="spinner-lg"></div>
          <p>Loading payment details...</p>
        </div>
      </div>
    );
  }

  /**
   * Render error state
   */
  if (error || !payment) {
    return (
      <div className={styles.container}>
        <div className={styles.errorCard}>
          <div className={styles.errorIcon}>❌</div>
          <h1 className={styles.errorTitle}>Payment Not Found</h1>
          <p className={styles.errorMessage}>
            {error || 'The payment you are looking for does not exist.'}
          </p>
          <div className={styles.errorActions}>
            <Link href="/payments" className="btn btn-primary">
              Back to Payments List
            </Link>
          </div>
        </div>
      </div>
    );
  }


  
  return (
    <div className={styles.container}>
      <div className={styles.card}>
        {/* Header with status */}
        <div className={styles.header}>
          <div className={styles.statusIcon}>
            {payment.transaction_status === 'completed' && '✅'}
            {payment.transaction_status === 'failed' && '❌'}
            {payment.transaction_status === 'processing' && '🔄'}
            {payment.transaction_status === 'pending' && '⏸'}
          </div>
          <h1 className={styles.title}>
            {payment.transaction_status === 'completed' && 'Payment Successful'}
            {payment.transaction_status === 'failed' && 'Payment Failed'}
            {payment.transaction_status === 'processing' && 'Payment Processing'}
            {payment.transaction_status === 'pending' && 'Payment Pending'}
          </h1>
          <p className={styles.subtitle}>
            {payment.transaction_status === 'completed' && 'Your payment has been completed successfully'}
            {payment.transaction_status === 'failed' && 'Payment processing failed'}
            {payment.transaction_status === 'processing' && 'Your payment is being processed...'}
            {payment.transaction_status === 'pending' && 'Waiting for confirmation'}
          </p>
        </div>

        {/* Transaction Details */}
        <div className={styles.details}>
          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Transaction ID</span>
            <span className={styles.detailValue}>
              <code>{payment.transaction_id}</code>
            </span>
          </div>

          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Amount</span>
            <span className={styles.detailValue}>
              {formatCurrency(payment.transaction_amount)} {payment.currency}
            </span>
          </div>

          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>From</span>
            <span className={styles.detailValue}>
              {payment.debtor_name}
              <br />
              <small>Account ID: {payment.debtor_account_id}</small>
            </span>
          </div>

          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>To</span>
            <span className={styles.detailValue}>
              {payment.creditor_name}
              <br />
              <small>Account ID: {payment.creditor_account_id}</small>
            </span>
          </div>

          {payment.description && (
            <div className={styles.detailRow}>
              <span className={styles.detailLabel}>Description</span>
              <span className={styles.detailValue}>{payment.description}</span>
            </div>
          )}

          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Status</span>
            <span className={styles.detailValue}>
              <StatusBadge status={payment.transaction_status} />
            </span>
          </div>

          <div className={styles.detailRow}>
            <span className={styles.detailLabel}>Created</span>
            <span className={styles.detailValue}>
              {formatDateTime(payment.created_at)}
            </span>
          </div>

          {payment.completed_at && (
            <div className={styles.detailRow}>
              <span className={styles.detailLabel}>Completed</span>
              <span className={styles.detailValue}>
                {formatDateTime(payment.completed_at)}
              </span>
            </div>
          )}
        </div>

        {/* Error Message (for failed payments) */}
        {payment.transaction_status === 'failed' && payment.error_message && (
          <div className={styles.errorSection}>
            <div className={styles.errorSectionTitle}>
              <span>⚠️</span>
              Failure Reason
            </div>
            <div className={styles.errorSectionContent}>
              {payment.error_message}
            </div>
            <div className={styles.errorSectionTitle}>
              <span>💡</span>
              Suggested Actions
            </div>
            <div className={styles.errorSectionContent}>
              <ul>
                <li>Check your account balance and top up if needed</li>
                <li>Verify recipient account information</li>
                <li>Try creating a new payment with updated details</li>
                <li>Contact support if the issue persists</li>
              </ul>
            </div>
          </div>
        )}

        {/* Status History */}
        {payment.logs && payment.logs.length > 0 && (
          <div className={styles.historySection}>
            <h2 className={styles.historyTitle}>Status History</h2>
            <div className={styles.timeline}>
              {payment.logs.map((log, index: number) => (
                <div key={index} className={styles.timelineItem}>
                  <div className={styles.timelineDot}>
                    {log.new_status === 'completed' && '✓'}
                    {log.new_status === 'failed' && '✗'}
                    {log.new_status === 'processing' && '⟳'}
                    {log.new_status === 'pending' && '○'}
                  </div>
                  <div className={styles.timelineContent}>
                    <div className={styles.timelineStatus}>
                      {getStatusText(log.new_status)}
                    </div>
                    <div className={styles.timelineTime}>
                      {formatDateTime(log.created_at)}
                    </div>
                    {log.error_message && (
                      <div className={styles.timelineError}>
                        Error: {log.error_message}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Info Message (for in-progress payments) */}
        {isInProgress && (
          <div className={styles.infoSection}>
            <span className={styles.infoIcon}>💡</span>
            <div className={styles.infoText}>
              <strong>Processing your payment...</strong>
              <br />
              Payments typically complete within 10 seconds. This page will update automatically.
              <br />
              <small className={styles.pollingInfo}>
                Checked {pollingCount} time{pollingCount !== 1 ? 's' : ''}
              </small>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className={styles.actions}>
          <Link href="/payments" className="btn btn-secondary">
            Back to List
          </Link>
          <Link href="/payments/new" className="btn btn-primary">
            Create New Payment
          </Link>
        </div>
      </div>
    </div>
  );
}