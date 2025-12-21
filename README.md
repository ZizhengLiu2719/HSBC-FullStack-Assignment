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

Full WorkFlow:

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
