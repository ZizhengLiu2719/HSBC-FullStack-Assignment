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
1.FastAPI(Python 3.11+)
2.Database:SQLite
3.ORM:SQLalchemy
4.Data validation: Pydantic V2
5.task list:Python asyncio + APScheduler
6.CORS handling: FastAPI CORS component

Full WorkFlow:

Stage 1:
1.User visted ->/Payments/new
2.frontEnd useEffect triger
3.API call: GET /api/accounts
