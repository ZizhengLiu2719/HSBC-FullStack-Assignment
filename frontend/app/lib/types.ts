/**
 * account information interface
 * to represent the account of the debtor or creditor
 */
//
export interface Account {
    account_id: string;        // account ID, like "ACC001"
    account_name: string;      // account name, like "Enterprise Operating Account"
    //correspond to backend account type:
    //- debtor_account_id
    //- creditor_account_id
    account_type: 'debtor' | 'creditor';  // account type: debtor or creditor
    balance: number;           // account balance
    created_at?: string;       // creation time (optional)
  }

  // payment transaction status
  export type PaymentStatus = 
    | 'pending'      // pending
    | 'processing'   // processing
    | 'completed'    // completed
    | 'failed';      // failed

  // payment transaction interface
  // to represent a complete payment record 
  export interface Payment {
    transaction_id: string;           // transaction ID
    debtor_account_id: string;        // debtor account ID
    creditor_account_id: string;      // creditor account ID
    debtor_name?: string;             // debtor name (optional, returned by backend)
    creditor_name?: string;           // creditor name (optional, returned by backend)
    transaction_amount: number;       // transaction amount
    currency: string;                 // currency type, default "CNY"
    transaction_status: PaymentStatus;// transaction status
    description?: string;             // payment description (optional)
    created_at: string;               // creation time
    updated_at?: string;              // update time (optional)
    completed_at?: string;            // completion time (optional)
    error_message?: string;           // error message (when failed)
  }
  
  /**
   * payment log interface
   * to record the change history of payment status
   */
  export interface PaymentLog {
    old_status: PaymentStatus | null; // old status (null when first created)
    new_status: PaymentStatus;        // new status
    error_message?: string;           // error message (optional)
    created_at: string;               // creation time
  }
  
  /**
   * create payment request interface
   * to represent the data sent when user submit create payment
   */
  export interface CreatePaymentRequest {
    debtor_account_id: string;
    creditor_account_id: string;
    transaction_amount: number;
    description?: string;
  }
  
  /**
   * API response interface
   * to represent the common structure of API response
   */
  export interface ApiResponse<T> {
    success: boolean;      // request is successful or not
    message?: string;      // message (optional)
    data?: T;              // data (when successful)
    error?: ApiError;      // error (when failed)
  }
  
  /**
   * API error interface
   * to represent the common structure of API error
   */
  export interface ApiError {
    code: string;          // error code, like "INSUFFICIENT_BALANCE"
    message: string;       // human readable error message
    details?: Record<string, unknown>; // additional error details (optional)
  }
  
  /**
   * payment list response interface
   * to represent the pagination information
   */
  export interface PaymentListResponse {
    items: Payment[];      // payment list
    pagination: {
        total: number;       // total records
      page: number;        // current page number
      limit: number;       // number of records per page
      total_pages: number; // total pages
    };
  }
  
  /**
   * payment detail response interface
   * to represent the payment information and log
   */
  export interface PaymentDetailResponse {
    transaction_id: string;
    debtor_account_id: string;
    creditor_account_id: string;
    debtor_name: string;
    creditor_name: string;
    transaction_amount: number;
    currency: string;
    transaction_status: PaymentStatus;
    description?: string;
    created_at: string;
    updated_at?: string;
    completed_at?: string;
    error_message?: string;
    logs: PaymentLog[];    // status change log
  }