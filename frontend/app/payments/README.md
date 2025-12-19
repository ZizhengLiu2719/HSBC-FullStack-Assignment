function of Payment list page:
1.present all payment record in the format of card
2.filter by state:pending/processing/completed/failed
3.separete the page
4.fast create by providing create payment
5.click the payment card into detail page

Data Flow:

1. Component mounts → fetch payments from API
2. User changes filter → fetch with filter parameter
3. Display payments using PaymentCard component

Loading State -> Fetch Data -> success/Error State

Full Workflow:
1.User visted /payments page
2.Compoent load
3.useEffect excute
4.present Loading State
5.API call: GET /api/payments?page=1&limit=10
6.if success:
showing payment list
if fail:
showing error message + retry button
7.after the process above, user can:
change filter: reload data
switch page: reload page
click card: enter the detailed page
click "Create Payment" button:create payment page
