How to start the Project?
1.BackEnd:
open terminal ->
cd backend ->
python run_server.py
//backend server start!
2.FrontEnd:
open another new terminal ->
cd frontend ->
npm run dev
//frontend start!
//now the whole project start!

FrontEnd Dev:

TechStack:
1.Next.js 14(APP Router) - the newest Routing from Next.js
2.Original CSS Modules

Create Next.js Project:
setting up by "npx create-next-app@latest frontend"

Page requirement from Assignment file:

- **Views/Components:**
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

Designed Pages(Based on the assignment requirement):
1.Creating a payments folder under APP folder
2.new page - payment input
3.preview page - payment preview(it is for comfirmation) 4.[id] page - showing the state
5.payments - payments list

Workflow: input -> preview -> comfirm -> state

Communication to Backend in Assignment file:

### 3.3 Frontend ↔ Backend Communication

- Use REST API calls for all interactions.
- How would you get payment status updates after initiation?

Designed Communication from Frontend to Backend:
1.Creating lib folder
2.creating api.ts - Encapsulation for API client
3.Checking the state update by Polling(because this is 1-2day project, I want to keep it simple,for a more mature solution, we can just WebSocker here for state updating)

Backend Dev:

Tech Stack:
1.framework: FastAPI 0.119.1
2.Database: SQLite(async) + SQLAlchemy 2.0 ORM
3.vaildation: Pydantic v2
4.Data validation: Pydantic V2
5.asynchronous: Uvicorn

Full WorkFlow(start from backend to frontend):

Backend workflow:

Stage 1(start the application):
1.run_server.py - launch the application
2.mainly.py - create FastAPI application
3.lifespan - manager initial database
4.init_db() - create table structure(accounts,payments,payment_logs)
5.loading CORS middleware - allow cross-domain access from the frontend 6.
6.register routing(/api/accounts, /api/payments)
7.server montior 0.0.0.0:8000

stage 2(get accounts list):
1.client request
2.FastAPI router (accounts.py::get_all_accounts)
3.import get_db() - create AsyncSession
4.SQLAlchemy: SELECT \* FROM accounts ORDER BY created_at DESC
5.ORM model: pydantic schema(AccountReponse)
6.return JSON:
{
"success": true,
"data": [
{
"account_id": "ACC001",
"account_name": "Main Operating Account",
"account_type": "debtor",
"balance": 100000.00,
"currency": "USD"
},
...
]
}

stage 3(create payment):
1.client post payment data
2.FastAPI Router(payments.py::create_payment)
3.Pydantic validation(createPaymentRequest)
valid amount > 0
valid account_id format
valid amount < 1000000
4.PaymentService.create_payment(db,payment_data)
5.Business verification
search debtor_account -> if not exist, throw AccountNotFoundException
search creditor_account -> if not exist, throw AccountNotFoundException
search if the account is same -> if not, throw SameAccountException
search if the balance is sufficient -> if not, InsufficientBalanceException
6.create payment_log
generate transaction_id(TXN_YYYYMMDD_XXXXXX)
create payment object(status = "pending")
db.add(payment)
db.flush() - get the Timestamp for created_at
7.create Initial log
create paymentLog(null->pending)
db.add(log)
db.commit()
8.launch backend stimulater
PaymentStatusSimulator.start_simulation(transaction_id) →
asyncio.create_task(stimulate payment process)
9.return response(status = pending)

stage 4(payment state simulate):
1.start_simulation(transcation_id)
2.asyncio.create_task(simulate_payment_processing)
3.phase 1: pending -> processing
asyncio.sleep(2 sec)
update_payment_status(transaction_id, "processing")
create PaymentLog (pending → processing)
4.Phase 2: processing → completed/failed
asyncio.sleep(3-6 sec random)
randomly decide completed/failed rate (90% success)
if success:
call PaymentService.complete_payment()
deduct the balance of debtor account
gain the balance of creditor account
update status = "completed"
set completed_at timestamp
create log(processing -> completed)
if fail:
call PaymentService.fail_payment()
update status = "failed"
set error_message (random error message)
set completed_at timestamp
create log(processing → failed)

stage 5(search payment status):
1.client request by polling
2.FastAPI Router (payments.py::get_payment_by_id)
3.PaymentService.get_payment_by_id(db, transaction_id, include_logs=True)
4.SQLAlchemy search:
SELECT \* FROM payments
WHERE transaction_id = ?
WITH eager loading (logs, debtor_account, creditor_account)
5.return full payment information + state update history:
{
"success": true,
"data": {
"transaction_id": "TXN_20250120_A3F9K2",
"transaction_status": "completed",
"transaction_amount": 1500.50,
"debtor_name": "Main Operating Account",
"creditor_name": "Office Supplies Ltd.",
"logs": [
{"old_status": null, "new_status": "pending", "created_at": "..."},
{"old_status": "pending", "new_status": "processing", "created_at": "..."},
{"old_status": "processing", "new_status": "completed", "created_at": "..."}
]
}
}

stage 6(get payment list):
1.client request
2.FastAPI Router(payments.py::get_payments)
parameter: page=1, limit=10, status="completed"
3.PaymentService.get_payments(db, page, limit, status)
4.SQLAlchemy search:
SELECT * FROM payments
WHERE transaction_status = ? (if there is)
ORDER BY created_at DESC
OFFSET (page-1)*limit
LIMIT limit
5.search total amount at the same time:
SELECT COUNT(\*) FROM payments WHERE ...
6.return page data:
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

FrontEnd Workflow:

stage 1(page loading):
1.user visit /payments/new
2.next.js render NewPaymentPage component
3.useEffect hook trigger
4.call fetchAccounts() - asynchronous function
5.API call: getAccounts() → fetch('http://localhost:8000/api/accounts')
6.backend return account list
7.frontend seperate debtor and creditor:
debtorAccounts = accounts.filter(acc => acc.account_type === 'debtor')
creditorAccounts = accounts.filter(acc => acc.account_type === 'creditor')
8.update component state:
setDebtorAccounts(debtors)
setCreditorAccounts(creditors)
setDebtorAccountId(debtors[0].account_id)
setLoading(false)
9.render the form

stage 2(user fill form):
User interaction:
1.select debtor account
onChange update debtorAccountId
showing the balance on real-time
2.select creditor account:
onChange update creditorAccountId
3.input Amount:
onChange update amount
onBlur trigger validation:
must > 0
at max 2 decimal
can not exceed usable balance
showing error message(if there is)
4.input Description(optional)
onChange update description
showing the text in real-time

stage 3(submit form -> preview):
1.user click "Next: preview" button
2.handlesubmit(e) trigger
3.e.preventDefault() - prevent the default form submit
4.validateForm() - frontend valid
check all must-fill string
check it is not the same account
check the legality of balance
check if the balance is suffient
5.if the validation fail:
setErrors({...})
return (stop submit)
6.if the validation success:
gather the data from form
search the account name(for showing)
construct paymentData object
7.store to sessionStroage:
sessionStorage.setItem('pendingPayment', JSON.stringify(paymentData))
8.change router:
router.push('/payments/preview')

stage 4(preview & comfirmation):
1.page load
2.previewPage component render
3.useState lazy initial:
const [paymentData] = useState(() => {
const stored = sessionStorage.getItem('pendingPayment');
return stored ? JSON.parse(stored) : null;
})
4.useEffect check:
if (!paymentData) {
router.push('/payments/new') # return if there is no data
}
5.rendering the preview page
From Account information
To Account information
Payment amount
description(if there is)
warning
6.user click "comfirm & submit payment" button
7.handleConfirm() trigger
8.setSubmitting(true) - prohibit button and showing loading animate
9.API call: createPayment(requestData):
POST http://localhost:8000/api/payments
Body: {
debtor_account_id: "ACC001",
creditor_account_id: "SUP001",
transaction_amount: 1500.50,
description: "..."
}
10.backend process(in backend stage 3)
11.backend return response:
{
"success": true,
"data": {
"transaction_id": "TXN_20250120_A3F9K2",
"transaction_status": "pending",
...
}
}
12.frontend receive response:
sessionStorage.removeItem('pendingPayment') - clean catch
router.push(`/payments/${response.transaction_id}`)

stage 5(state tracking):
1.page loading
2.paymentDetailPage component rendering
3.extract URL from transcation_id:
const params = useParams()
const transactionId = params.id
4.get initial data:
useEffect(() => {
fetchPayment()  
}, [fetchPayment])
↓
fetchPayment():
API call: getPaymentById(transactionId)
GET http://localhost:8000/api/payments/TXN_20250120_A3F9K2
setPayment(data)
setLoading(false)
5.polling machanism:
useEffect(() => {
if (loading || error || !payment) return
if (payment.transaction_status === 'completed') return
if (payment.transaction_status === 'failed') return

const intervalId = setInterval(() => {
fetchPayment() # 每 2 秒重新获取数据
}, 2000)

return () => clearInterval(intervalId)
}, [loading, error, payment, fetchPayment])
6.real-time update process:
every 2 sec:
fetchPayment()
API call the newest state
setPayment(newData)
React re-rendering
if user see the change of state:
pending → processing → completed/failed
if reach the final state:
stop polling
7.UI presentation:
based on transaction_status rendering:

- pending: "Payment Pending"
- processing: "Payment Processing"
- completed: "Payment Successful"
- failed: "Payment Failed" + fail reason + suggest operation
  ↓
  showing state history (Timeline):
  logs.map(log =>
  pending → processing → completed
  )

stage 6(payment list):
1.page loading
2.paymentsPage component rendering
3.useState initial:
payments: []
statusFilter: 'all'
currentPage: 1
totalPages: 1
4.useEffect trigger (dependency: statusFilter, currentPage)
5.fetchPayments():
construct inquiry parameter:
params = {
page: currentPage,
limit: 10,
status: statusFilter !== 'all' ? statusFilter : undefined
}
API call: getPayments(params)
GET http://localhost:8000/api/payments?page=1&limit=10&status=completed
setPayments(response.items)
setTotalPages(response.pagination.total_pages)
6.rendering page:
page head(title + create payment button)
filter(state drop-down selection)
payment card grid(PaymentCard component)
paging control(prev page/next page/page number)
7.user interaction:
change the filter:
handleFilterChange()
setStatusFilter(newValue)
setCurrentPage(1)  
 useEffect - re-trigger
Click to paginate:
handlePageChange(page)
setCurrentPage(page)
window.scrollTo(top)
useEffect
Click payment card:
redirect to /payments/{transaction_id}
