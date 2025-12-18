// API client
// encapsulate all communication with the backend


import type {
    Account,
    ApiResponse,
    CreatePaymentRequest,
    Payment,
    PaymentDetailResponse,
    PaymentListResponse,
} from './types';
  
  // API base URL
  // development environment: backend runs on port 8000
  // production environment: can be read from environment variables
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  /**
   * generic fetch wrapper
   * handle errors, add common headers etc.
   */
  async function fetchAPI<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // build full URL
    const url = `${API_BASE_URL}${endpoint}`;
    
    // merge default config and incoming config
    const config: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };
    
    try {
      // send request
      const response = await fetch(url, config);
      
      // parse JSON
      const data = await response.json();
      
      // if HTTP status code is not 2xx, throw error
      if (!response.ok) {
        throw {
          status: response.status,
          ...data,
        };
      }
      
      return data;
    } catch (error) {
      // network error or other error
      console.error('API Error:', error);
      throw error;
    }
  }
  
  // account related API
  
  /**
   * get all accounts list
   * GET /api/accounts
   */
  export async function getAccounts(): Promise<Account[]> {
    const response = await fetchAPI<ApiResponse<Account[]>>('/api/accounts');
    return response.data || [];
  }
  
  /**
   * get single account by ID
   */
  export async function getAccountById(accountId: string): Promise<Account | null> {
    const accounts = await getAccounts();
    return accounts.find(acc => acc.account_id === accountId) || null;
  }
  
  // payment related API
  
  /**
   * create new payment
   * POST /api/payments
   */
  export async function createPayment(
    payment: CreatePaymentRequest
  ): Promise<Payment> {
    const response = await fetchAPI<ApiResponse<Payment>>('/api/payments', {
      method: 'POST',
      body: JSON.stringify(payment),
    });
    
    if (!response.success || !response.data) {
      throw response.error || new Error('create payment failed');
    }
    
    return response.data;
  }
  
  /**
   * get payment detail
   * GET /api/payments/{transactionId}
   */
  export async function getPaymentById(
    transactionId: string
  ): Promise<PaymentDetailResponse> {
    const response = await fetchAPI<ApiResponse<PaymentDetailResponse>>(
      `/api/payments/${transactionId}`
    );
    
    if (!response.success || !response.data) {
      throw response.error || new Error('get payment detail failed');
    }
    
    return response.data;
  }
  
  /**
   * get payment list (paged)
   * GET /api/payments?page=1&limit=10&status=completed
   */
  export async function getPayments(params: {
    page?: number;
    limit?: number;
    status?: string;
  } = {}): Promise<PaymentListResponse> {
    // build query string
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.status) queryParams.append('status', params.status);
    
    const queryString = queryParams.toString();
    const endpoint = `/api/payments${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetchAPI<ApiResponse<PaymentListResponse>>(endpoint);
    
    if (!response.success || !response.data) {
        throw response.error || new Error('get payment list failed');
    }
    
    return response.data;
  }