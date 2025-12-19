//Nest.js routing
import Link from 'next/link';
//Helper functions
import { formatCurrency, formatDateTime } from '../../lib/utils';
//Types
import type { Payment } from '../../lib/types';
//StatusBadge
import StatusBadge from '../StatusBadge/StatusBadge';
//Styles
import styles from './PaymentCard.module.css';


//Payment type already defined in types.ts
interface PaymentCardProps {
  payment: Payment;
}

export default function PaymentCard({ payment }: PaymentCardProps) {
  return (
    <div className={styles.card}>
      {/* Header: Transaction ID and Status */}
      <div className={styles.header}>
        <div className={styles.transactionId}>
          {payment.transaction_id}
        </div>
        <StatusBadge status={payment.transaction_status} />
      </div>

      {/* Body: Main payment information */}
      <div className={styles.body}>
        {/* Amount and recipient */}
        <div className={styles.amount}>
          {formatCurrency(payment.transaction_amount)}
          <span className={styles.arrow}>→</span>
          <span className={styles.recipient}>
            {payment.creditor_name || payment.creditor_account_id}
          </span>
        </div>

        {/* Description (if available) */}
        {payment.description && (
          <div className={styles.description}>
            {payment.description}
          </div>
        )}
      </div>

      {/* Footer: Date and action link */}
      <div className={styles.footer}>
        <div className={styles.date}>
          {formatDateTime(payment.created_at)}
        </div>
        
        <Link 
          href={`/payments/${payment.transaction_id}`}
          className={styles.link}
        >
          View Details →
        </Link>
      </div>
    </div>
  );
}