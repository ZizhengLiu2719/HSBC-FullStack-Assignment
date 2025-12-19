'use client';  // Client Component for interactivity

import PaymentCard from '@/app/components/PaymentCard/PaymentCard';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { getPayments } from '../lib/api';
import type { Payment } from '../lib/types';
import styles from './page.module.css';


export default function PaymentsPage() {
  
  // Payments data from API
  const [payments, setPayments] = useState<Payment[]>([]);
  
  // Loading state
  const [loading, setLoading] = useState(true);
  
  // Error state
  const [error, setError] = useState<string | null>(null);
  
  // Current filter (all, pending, processing, completed, failed)
  const [statusFilter, setStatusFilter] = useState<string>('all');
  
  // Current page number
  const [currentPage, setCurrentPage] = useState(1);
  
  // Total pages (from API response)
  const [totalPages, setTotalPages] = useState(1);

  
  /**
   * Fetch payments from API
   * Called when component mounts or filter/page changes
   */
  useEffect(() => {
    async function fetchPayments() {
      try {
        setLoading(true);
        setError(null);
        
        // Build API request parameters
        const params: {
          page: number;
          limit: number;
          status?: string;
        } = {
          page: currentPage,
          limit: 10,  // 10 payments per page
        };
        
        // Add status filter if not "all"
        if (statusFilter !== 'all') {
          params.status = statusFilter;
        }
        
        // Call API
        const response = await getPayments(params);
        
        // Update state
        setPayments(response.items);
        setTotalPages(response.pagination.total_pages);
        
      } catch (err) {
        const errorObj = err instanceof Error
          ? err
          : new Error(typeof err === 'string' ? err : 'Unknown error');
        console.error('Failed to fetch payments:', errorObj);
        setError(errorObj.message || 'Failed to load payments');
      } finally {
        setLoading(false);
      }
    }
    
    fetchPayments();
  }, [statusFilter, currentPage]);  // Re-run when filter or page changes

  
  /**
   * Handle status filter change
   */
  const handleFilterChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(event.target.value);
    setCurrentPage(1);  // Reset to page 1 when filter changes
  };

  /**
   * Handle page change
   */
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // Scroll to top when page changes
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  
  /**
   * Render loading state
   */
  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className="spinner-lg"></div>
          <p>Loading payments...</p>
        </div>
      </div>
    );
  }

  /**
   * Render error state
   */
  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>⚠️ Error</h2>
          <p>{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="btn btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  
  return (
    <div className={styles.container}>
      {/* Page Header */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <h1 className={styles.title}>📊 Payment Management</h1>
          <p className={styles.subtitle}>
            View and track all your payment transactions
          </p>
        </div>
        
        <div className={styles.headerRight}>
          <Link href="/payments/new" className="btn btn-primary">
            + Create Payment
          </Link>
        </div>
      </div>

      {/* Filters Section */}
      <div className={styles.filters}>
        <div className={styles.filterGroup}>
          <label htmlFor="status-filter" className={styles.filterLabel}>
            Filter by Status:
          </label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={handleFilterChange}
            className="form-select"
          >
            <option value="all">All Payments</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        {/* Show count of results */}
        <div className={styles.resultCount}>
          {payments.length === 0 ? (
            'No payments found'
          ) : (
            `Showing ${payments.length} payment${payments.length !== 1 ? 's' : ''}`
          )}
        </div>
      </div>

      {/* Payments List */}
      {payments.length === 0 ? (
        /* Empty State */
        <div className={styles.empty}>
          <div className={styles.emptyIcon}>📭</div>
          <h2 className={styles.emptyTitle}>No Payments Found</h2>
          <p className={styles.emptyText}>
            {statusFilter === 'all' 
              ? "You haven't created any payments yet."
              : `No ${statusFilter} payments found.`
            }
          </p>
          <Link href="/payments/new" className="btn btn-primary">
            Create Your First Payment
          </Link>
        </div>
      ) : (
        /* Payments Grid */
        <div className={styles.paymentsGrid}>
          {payments.map((payment) => (
            <PaymentCard key={payment.transaction_id} payment={payment} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className={styles.pagination}>
          {/* Previous Button */}
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className={`${styles.pageButton} ${currentPage === 1 ? styles.disabled : ''}`}
          >
            « Previous
          </button>

          {/* Page Numbers */}
          <div className={styles.pageNumbers}>
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => handlePageChange(page)}
                className={`${styles.pageNumber} ${
                  page === currentPage ? styles.active : ''
                }`}
              >
                {page}
              </button>
            ))}
          </div>

          {/* Next Button */}
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className={`${styles.pageButton} ${
              currentPage === totalPages ? styles.disabled : ''
            }`}
          >
            Next »
          </button>
        </div>
      )}
    </div>
  );
}