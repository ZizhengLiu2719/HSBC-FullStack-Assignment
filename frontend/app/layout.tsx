import type { Metadata } from 'next';
import Header from './components/Header/Header';
import './globals.css';


// Metadata for SEO and browser tabs
export const metadata: Metadata = {
  title: 'PaymentHub - Business Payment Management',
  description: 'Manage and track payments to suppliers with ease. Create, review, and monitor payment transactions.',
  keywords: 'payment, business, supplier, transaction, finance',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        {/* You can add additional meta tags here if needed */}
      </head>
      <body>
        {/* Header component - appears on all pages */}
        <Header />
        
        {/* Main content area */}
        <main className="main-content">
          {children}
        </main>
        
        {/* Optional: Footer component */}
        <footer className="footer">
          <div className="container">
            <p className="text-center text-muted">
              © 2024 PaymentHub. Built for small business payments.
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
