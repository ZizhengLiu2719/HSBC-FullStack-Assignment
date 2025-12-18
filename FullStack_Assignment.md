# Take-Home Assignment

**Role:** Full Stack Engineer & UI/UX  
**Time Expectation:** 1-2 days
**Primary Stack:** Next.js / React (frontend), Python (backend)

---

## 1. Context

Small business owners often need to initiate and track payments to suppliers. Your task is to build a minimal backend and frontend full-stack app that allows a user to:

- Initiate a payment
- Review and confirm payment details before execution
- Track payment status
- Clearly understand errors and next steps

---

## 2. User Scenario

A small business owner wants to pay a supplier. The application should enable the user to:

1. Enter a payment request
2. Review the parsed payment details (amount, payer, payee, date)
3. Confirm or edit the payment before sending
4. View the payment status (e.g., processing, completed, failed)
5. Understand what went wrong if there is an error

---

## 3. Assignment Requirements

### 3.1 Backend: Payments & APIs

- **Database:**  
  Use any storage of choice to persist payment transactions with the following fields:
  - `debtor_account_id`
  - `creditor_account_id`
  - `transaction_id`
  - `transaction_amount`
  - `transaction_date`
  - `transaction_status`

- **API Requirements:**  
  Your backend should expose at least the following endpoints:

  1. **POST `/api/payments`**
      - Accepts structured payment details.
      - Creates a new payment transaction.
      - Returns the transaction ID and details.

  2. **GET `/api/payments/{transaction_id}`**
      - Returns the status and details of a specific payment.
      - Simulate status changes (e.g., processing → completed/failed after a delay).

### 3.2 Frontend: Next.js / React Application

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

- **UX Expectations:**
  - The user always knows what the system interprets from their input.
  - No irreversible actions without explicit confirmation.
  - Clear, simple, and intuitive flows.

### 3.3 Frontend ↔ Backend Communication

- Use REST API calls for all interactions.
- How would you get payment status updates after initiation?

---

## 4. Deliverables

1. **A working application** (frontend + backend)
2. **README** including:
   - Architecture overview
   - API contracts
   - UX decisions and tradeoffs
   - What you would improve with more time
   - Instructions to run locally
   - Assumptions made

---

## 5. Instructions

- Focus on intuitive user journeys, clear input structuring, effective API integration, and frontend design.
- Keep the codebase simple and well-structured.
- Submit your code and README as a GitHub repository.