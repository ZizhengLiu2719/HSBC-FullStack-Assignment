import { getStatusText, getStatusColor } from '../../lib/utils';
import styles from './StatusBadge.module.css';



interface StatusBadgeProps {
  status: string;  // 'pending' | 'processing' | 'completed' | 'failed'
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  // Get display text (e.g., "completed")
  const text = getStatusText(status);
  
  // Get color class (e.g., "success" for green)
  const colorClass = getStatusColor(status);

  return (
    <span className={`${styles.badge} ${styles[colorClass]}`}>
      {/* Icon based on status */}
      <span className={styles.icon}>
        {status === 'completed' && '✓'}
        {status === 'failed' && '✗'}
        {status === 'processing' && '⟳'}
        {status === 'pending' && '⏸'}
      </span>
      
      {/* Status text */}
      <span className={styles.text}>
        {text}
      </span>
    </span>
  );
}