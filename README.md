# HSBC Full-Stack Payment System

A full-stack payment management system built with FastAPI (Backend) and Next.js 14 (Frontend).

---

## 🚀 Quick Start

### 1. Backend Setup

Open terminal and run:

```bash
cd backend
python run_server.py
```

Backend server will start at `http://localhost:8000`

### 2. Frontend Setup

Open another terminal and run:

```bash
cd frontend
npm run dev
```

Frontend will start at `http://localhost:3000`

**Now the whole project is running!**

---

## 💻 Frontend Development

### Tech Stack

1. **Next.js 14 (APP Router)** - The newest routing from Next.js
2. **Original CSS Modules** - For component styling

### Project Setup

```bash
npx create-next-app@latest frontend
```

### Page Requirements from Assignment

#### Views/Components:

- **Payment Initiation Input:**  
  User enters a payment request. You can choose between a structured / natural language approach.

- **Payment Preview:**  
  Display parsed payment details for review and editing.

- **Confirmation Step:**  
  User must confirm before payment is sent.

- **Status Display:**  
  Show payment progress and final status.

- **Error Handling:**  
  Provide clear messaging and recovery options if something goes wrong.

### Designed Pages

Based on the assignment requirements:

1. Creating a `payments` folder under APP folder
2. `new` page - payment input
3. `preview` page - payment preview (for confirmation)
4. `[id]` page - showing the state
5. `payments` - payments list

### Workflow

```
input → preview → confirm → state
```

### Frontend ↔ Backend Communication

From Assignment file:

> **3.3 Frontend ↔ Backend Communication**
>
> - Use REST API calls for all interactions.
> - How would you get payment status updates after initiation?

#### Designed Communication Strategy:

1. Creating `lib` folder
2. Creating `api.ts` - Encapsulation for API client
3. Checking the state update by **Polling** (because this is a 1-2 day project, I want to keep it simple; for a more mature solution, we can use WebSocket here for state updating)

---

## 🔧 Backend Development

### Tech Stack

| Component       | Technology                          |
| --------------- | ----------------------------------- |
| Framework       | FastAPI 0.119.1                     |
| Database        | SQLite (async) + SQLAlchemy 2.0 ORM |
| Validation      | Pydantic v2                         |
| Data Validation | Pydantic V2                         |
| Asynchronous    | Uvicorn                             |

---

## 📊 Full Workflow (Backend to Frontend)

### Backend Workflow

#### Stage 1: Start the Application

1. `run_server.py` - launch the application
2. `main.py` - create FastAPI application
3. `lifespan` - manager initial database
4. `init_db()` - create table structure (accounts, payments, payment_logs)
5. Loading CORS middleware - allow cross-domain access from the frontend
6. Register routing (`/api/accounts`, `/api/payments`)
7. Server monitor `0.0.0.0:8000`

#### Stage 2: Get Accounts List

1. Client request
2. FastAPI router (`accounts.py::get_all_accounts`)
3. Import `get_db()` - create AsyncSession
4. SQLAlchemy: `SELECT * FROM accounts ORDER BY created_at DESC`
5. ORM model: Pydantic schema (`AccountResponse`)
6. Return JSON:

```json
{
  "success": true,
  "data": [
    {
      "account_id": "ACC001",
      "account_name": "Main Operating Account",
      "account_type": "debtor",
      "balance": 100000.0,
      "currency": "USD"
    }
  ]
}
```

#### Stage 3: Create Payment

1. Client post payment data
2. FastAPI Router (`payments.py::create_payment`)
3. **Pydantic validation** (`CreatePaymentRequest`)

   - Valid amount > 0
   - Valid account_id format
   - Valid amount < 1000000

4. **PaymentService.create_payment(db, payment_data)**

5. **Business verification:**

   - Search `debtor_account` → if not exist, throw `AccountNotFoundException`
   - Search `creditor_account` → if not exist, throw `AccountNotFoundException`
   - Search if the account is same → if not, throw `SameAccountException`
   - Search if the balance is sufficient → if not, `InsufficientBalanceException`

6. **Create payment log:**

   - Generate `transaction_id` (TXN_YYYYMMDD_XXXXXX)
   - Create payment object (status = "pending")
   - `db.add(payment)`
   - `db.flush()` - get the timestamp for created_at

7. **Create initial log:**

   - Create `PaymentLog` (null → pending)
   - `db.add(log)`
   - `db.commit()`

8. **Launch backend simulator:**

   - `PaymentStatusSimulator.start_simulation(transaction_id)` →
   - `asyncio.create_task(simulate payment process)`

9. Return response (status = pending)

#### Stage 4: Payment State Simulate

1. `start_simulation(transaction_id)`
2. `asyncio.create_task(simulate_payment_processing)`

3. **Phase 1: pending → processing**

   - `asyncio.sleep(2 sec)`
   - `update_payment_status(transaction_id, "processing")`
   - Create `PaymentLog` (pending → processing)

4. **Phase 2: processing → completed/failed**

   - `asyncio.sleep(3-6 sec random)`
   - Randomly decide completed/failed rate (90% success)

   **If success:**

   - Call `PaymentService.complete_payment()`
   - Deduct the balance of debtor account
   - Gain the balance of creditor account
   - Update status = "completed"
   - Set `completed_at` timestamp
   - Create log (processing → completed)

   **If fail:**

   - Call `PaymentService.fail_payment()`
   - Update status = "failed"
   - Set `error_message` (random error message)
   - Set `completed_at` timestamp
   - Create log (processing → failed)

#### Stage 5: Search Payment Status

1. Client request by polling
2. FastAPI Router (`payments.py::get_payment_by_id`)
3. `PaymentService.get_payment_by_id(db, transaction_id, include_logs=True)`
4. SQLAlchemy search:

```sql
SELECT * FROM payments
WHERE transaction_id = ?
WITH eager loading (logs, debtor_account, creditor_account)
```

5. Return full payment information + state update history:

```json
{
  "success": true,
  "data": {
    "transaction_id": "TXN_20250120_A3F9K2",
    "transaction_status": "completed",
    "transaction_amount": 1500.5,
    "debtor_name": "Main Operating Account",
    "creditor_name": "Office Supplies Ltd.",
    "logs": [
      { "old_status": null, "new_status": "pending", "created_at": "..." },
      {
        "old_status": "pending",
        "new_status": "processing",
        "created_at": "..."
      },
      {
        "old_status": "processing",
        "new_status": "completed",
        "created_at": "..."
      }
    ]
  }
}
```

#### Stage 6: Get Payment List

1. Client request
2. FastAPI Router (`payments.py::get_payments`)
3. Parameters: `page=1, limit=10, status="completed"`
4. `PaymentService.get_payments(db, page, limit, status)`
5. SQLAlchemy search:

```sql
SELECT * FROM payments
WHERE transaction_status = ? (if there is)
ORDER BY created_at DESC
OFFSET (page-1)*limit
LIMIT limit
```

6. Search total amount at the same time:

```sql
SELECT COUNT(*) FROM payments WHERE ...
```

7. Return page data:

```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "total": 50,
      "page": 1,
      "limit": 10,
      "total_pages": 5
    }
  }
}
```

---

## 🎨 Frontend Workflow

### Stage 1: Page Loading

1. User visit `/payments/new`
2. Next.js render `NewPaymentPage` component
3. `useEffect` hook trigger
4. Call `fetchAccounts()` - asynchronous function
5. API call: `getAccounts()` → `fetch('http://localhost:8000/api/accounts')`
6. Backend return account list
7. Frontend separate debtor and creditor:

```javascript
debtorAccounts = accounts.filter((acc) => acc.account_type === "debtor");
creditorAccounts = accounts.filter((acc) => acc.account_type === "creditor");
```

8. Update component state:

```javascript
setDebtorAccounts(debtors);
setCreditorAccounts(creditors);
setDebtorAccountId(debtors[0].account_id);
setLoading(false);
```

9. Render the form

### Stage 2: User Fill Form

**User interaction:**

1. **Select debtor account:**

   - `onChange` update `debtorAccountId`
   - Showing the balance in real-time

2. **Select creditor account:**

   - `onChange` update `creditorAccountId`

3. **Input Amount:**

   - `onChange` update `amount`
   - `onBlur` trigger validation:
     - Must > 0
     - At max 2 decimal
     - Cannot exceed usable balance
   - Showing error message (if there is)

4. **Input Description (optional):**
   - `onChange` update `description`
   - Showing the text in real-time

### Stage 3: Submit Form → Preview

1. User click "Next: Preview" button
2. `handleSubmit(e)` trigger
3. `e.preventDefault()` - prevent the default form submit
4. `validateForm()` - frontend validation:

   - Check all must-fill string
   - Check it is not the same account
   - Check the legality of balance
   - Check if the balance is sufficient

5. **If the validation fails:**

   - `setErrors({...})`
   - `return` (stop submit)

6. **If the validation succeeds:**

   - Gather the data from form
   - Search the account name (for showing)
   - Construct `paymentData` object

7. Store to `sessionStorage`:

```javascript
sessionStorage.setItem("pendingPayment", JSON.stringify(paymentData));
```

8. Change router:

```javascript
router.push("/payments/preview");
```

### Stage 4: Preview & Confirmation

1. Page load
2. `PreviewPage` component render
3. `useState` lazy initial:

```javascript
const [paymentData] = useState(() => {
  const stored = sessionStorage.getItem("pendingPayment");
  return stored ? JSON.parse(stored) : null;
});
```

4. `useEffect` check:

```javascript
if (!paymentData) {
  router.push("/payments/new"); // return if there is no data
}
```

5. Rendering the preview page:

   - From Account information
   - To Account information
   - Payment amount
   - Description (if there is)
   - Warning

6. User click "Confirm & Submit Payment" button
7. `handleConfirm()` trigger
8. `setSubmitting(true)` - prohibit button and showing loading animate

9. API call: `createPayment(requestData)`:

```javascript
POST http://localhost:8000/api/payments
Body: {
  debtor_account_id: "ACC001",
  creditor_account_id: "SUP001",
  transaction_amount: 1500.50,
  description: "..."
}
```

10. Backend process (see Backend Stage 3)

11. Backend return response:

```json
{
  "success": true,
  "data": {
    "transaction_id": "TXN_20250120_A3F9K2",
    "transaction_status": "pending",
    ...
  }
}
```

12. Frontend receive response:

```javascript
sessionStorage.removeItem("pendingPayment"); // clean cache
router.push(`/payments/${response.transaction_id}`);
```

### Stage 5: State Tracking

1. Page loading
2. `PaymentDetailPage` component rendering
3. Extract URL from `transaction_id`:

```javascript
const params = useParams();
const transactionId = params.id;
```

4. Get initial data:

```javascript
useEffect(() => {
  fetchPayment()
}, [fetchPayment])

// fetchPayment():
API call: getPaymentById(transactionId)
GET http://localhost:8000/api/payments/TXN_20250120_A3F9K2
setPayment(data)
setLoading(false)
```

5. **Polling mechanism:**

```javascript
useEffect(() => {
  if (loading || error || !payment) return;
  if (payment.transaction_status === "completed") return;
  if (payment.transaction_status === "failed") return;

  const intervalId = setInterval(() => {
    fetchPayment(); // Re-fetch data every 2 seconds
  }, 2000);

  return () => clearInterval(intervalId);
}, [loading, error, payment, fetchPayment]);
```

6. **Real-time update process:**

   - Every 2 seconds:
     - `fetchPayment()`
     - API call the newest state
     - `setPayment(newData)`
     - React re-rendering
   - If user sees the change of state:
     - `pending → processing → completed/failed`
   - If reach the final state:
     - Stop polling

7. **UI presentation:**

Based on `transaction_status` rendering:

- **pending:** "Payment Pending"
- **processing:** "Payment Processing"
- **completed:** "Payment Successful"
- **failed:** "Payment Failed" + fail reason + suggest operation

Showing state history (Timeline):

```javascript
logs.map(log =>
  pending → processing → completed
)
```

### Stage 6: Payment List

1. Page loading
2. `PaymentsPage` component rendering
3. `useState` initial:

```javascript
payments: [];
statusFilter: "all";
currentPage: 1;
totalPages: 1;
```

4. `useEffect` trigger (dependency: `statusFilter`, `currentPage`)

5. `fetchPayments()`:

```javascript
// Construct inquiry parameter:
params = {
  page: currentPage,
  limit: 10,
  status: statusFilter !== 'all' ? statusFilter : undefined
}

// API call:
getPayments(params)
GET http://localhost:8000/api/payments?page=1&limit=10&status=completed

setPayments(response.items)
setTotalPages(response.pagination.total_pages)
```

6. Rendering page:

   - Page head (title + create payment button)
   - Filter (state drop-down selection)
   - Payment card grid (`PaymentCard` component)
   - Paging control (prev page/next page/page number)

7. **User interaction:**

   **Change the filter:**

   ```javascript
   handleFilterChange();
   setStatusFilter(newValue);
   setCurrentPage(1);
   // useEffect re-trigger
   ```

   **Click to paginate:**

   ```javascript
   handlePageChange(page);
   setCurrentPage(page);
   window.scrollTo(top);
   // useEffect re-trigger
   ```

   **Click payment card:**

   ```javascript
   // Redirect to /payments/{transaction_id}
   ```

---

## 📄 License

This project is part of HSBC Full-Stack Assignment.
