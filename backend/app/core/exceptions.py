"""
Custom Exception Classes

Application-specific exceptions for better error handling.
"""


class PaymentSystemException(Exception):
    """Base exception for all payment system errors"""
    def __init__(self, message: str, code: str = "SYSTEM_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AccountNotFoundException(PaymentSystemException):
    """Raised when an account is not found"""
    def __init__(self, account_id: str):
        super().__init__(
            message=f"Account '{account_id}' not found",
            code="ACCOUNT_NOT_FOUND"
        )
        self.account_id = account_id


class InsufficientBalanceException(PaymentSystemException):
    """Raised when account balance is insufficient"""
    def __init__(self, account_id: str, available: float, required: float):
        super().__init__(
            message=f"Insufficient balance in account '{account_id}'",
            code="INSUFFICIENT_BALANCE"
        )
        self.account_id = account_id
        self.available_balance = available
        self.required_amount = required


class SameAccountException(PaymentSystemException):
    """Raised when debtor and creditor are the same account"""
    def __init__(self, account_id: str):
        super().__init__(
            message="Debtor and creditor cannot be the same account",
            code="SAME_ACCOUNT_ERROR"
        )
        self.account_id = account_id


class PaymentNotFoundException(PaymentSystemException):
    """Raised when a payment is not found"""
    def __init__(self, transaction_id: str):
        super().__init__(
            message=f"Payment '{transaction_id}' not found",
            code="PAYMENT_NOT_FOUND"
        )
        self.transaction_id = transaction_id


class InvalidStatusTransitionException(PaymentSystemException):
    """Raised when trying to perform an invalid status transition"""
    def __init__(self, old_status: str, new_status: str):
        super().__init__(
            message=f"Invalid status transition from '{old_status}' to '{new_status}'",
            code="INVALID_STATUS_TRANSITION"
        )
        self.old_status = old_status
        self.new_status = new_status
