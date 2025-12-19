'use client';  // This is a Client Component (uses interactivity)

//Use link for client-side navigation: only update the changing part while clicking, not the whole page
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Header.module.css';


export default function Header() {
  // Get current path to highlight active navigation
  const pathname = usePathname();

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        {/* Left side: Logo and Title */}
        <div className={styles.brand}>
          <Link href="/" className={styles.logo}>
            {/* 
              💼 Icon (you can replace with actual logo image)
              We use emoji for simplicity in this assignment
            */}
            <span className={styles.logoIcon}>💼</span>
            <span className={styles.logoText}>PaymentHub</span>
          </Link>
        </div>

        {/* Right side: Navigation */}
        <nav className={styles.nav}>
          <Link 
            href="/payments" 
            className={`${styles.navLink} ${pathname === '/payments' ? styles.active : ''}`}
          >
            Payments
          </Link>
          
          <Link 
            href="/payments/new" 
            className={`${styles.navButton} btn btn-primary btn-sm`}
          >
            + Create Payment
          </Link>
        </nav>
      </div>
    </header>
  );
}