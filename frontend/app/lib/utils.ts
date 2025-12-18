// utility functions
// provide commonly used helper functions


//default currency is USD
export function formatCurrency(amount: number, currency: string = '$'): string {
    return `${currency}${amount.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  }
  
  /**
   * format date time
   * convert ISO date string to readable format
   */
  export function formatDateTime(dateString: string): string {
    const date = new Date(dateString);
    
    // get each part of the date    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }
  
  /**
   * format date (without time)
   */
  export function formatDate(dateString: string): string {
    const date = new Date(dateString);
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
  }
  
  /**
   * get status text
   */
  export function getStatusText(status: string): string {
    const statusMap: Record<string, string> = {
      pending: 'pending',
      processing: 'processing',
      completed: 'completed',
      failed: 'failed',
    };
    
    return statusMap[status] || status;
  }
  
  /**
   * get status color
   */
  export function getStatusColor(status: string): string {
    const colorMap: Record<string, string> = {
      pending: 'warning',
      processing: 'info',
      completed: 'success',
      failed: 'danger',
    };
    
    return colorMap[status] || 'default';
  }
  
  /**
   * validate amount format
   * check if the amount is valid (positive number, up to 2 decimal places)
   */
  export function validateAmount(amount: string): string | null {
    // check if the amount is empty
    if (!amount || amount.trim() === '') {
      return 'please enter the amount';
    }
    
    // convert to number
    const num = parseFloat(amount);
    
    // check if the amount is a valid number
    if (isNaN(num)) {
      return 'please enter a valid number';
    }
    
    // check if the amount is positive
    if (num <= 0) {
      return 'the amount must be greater than 0';
    }
    
    // check if the amount has up to 2 decimal places
    const decimalPart = amount.split('.')[1];
    if (decimalPart && decimalPart.length > 2) {
      return 'the amount can only have up to 2 decimal places';
    }
    
    return null; // validation passed
  }
  
  /**
    * debounce function
   * delay the execution of the function, if the function is called again within the delay period, the timer will be reset
   * commonly used for search input etc.
   */
  export function debounce<T extends (...args: unknown[]) => unknown>(
    func: T,
    delay: number
  ): (...args: Parameters<T>) => void {
    let timeoutId: ReturnType<typeof setTimeout>;
    
    return function(...args: Parameters<T>) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    };
  }
  
  /**
   * generate unique ID
   * simple unique ID generator (for temporary data)
   */
  export function generateId(): string {
    return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }