import { redirect } from 'next/navigation';

/**
 * Home Page
 * 
 * Redirects to the payments list page since that's the main feature of the application.
 * This is a Server Component that performs a server-side redirect.
 */
export default function Home() {
  redirect('/payments');
}
