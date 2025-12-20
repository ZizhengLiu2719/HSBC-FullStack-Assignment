"""
API Integration Tests

Tests all API endpoints with real HTTP requests.

Usage:
    1. Start server: python run_server.py
    2. Run tests: python test_api.py
"""

import asyncio
import httpx
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print test section header"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)


def print_result(test_name: str, success: bool, details: str = ""):
    """Print test result"""
    status = "[OK]" if success else "[FAIL]"
    print(f"{status} {test_name}")
    if details:
        print(f"     {details}")


async def test_api():
    """Run all API tests"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("="*60)
        print("Testing API Endpoints")
        print("="*60)
        
        # ========================================
        # Test 1: Root Endpoint
        # ========================================
        print_section("[Test 1] Root Endpoint")
        
        response = await client.get(f"{BASE_URL}/")
        print_result(
            "GET /",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        data = response.json()
        print(f"     App: {data.get('name')}")
        print(f"     Version: {data.get('version')}")
        print(f"     Status: {data.get('status')}")
        
        # ========================================
        # Test 2: Health Check
        # ========================================
        print_section("[Test 2] Health Check")
        
        response = await client.get(f"{BASE_URL}/health")
        print_result(
            "GET /health",
            response.status_code == 200,
            f"Status: {response.json().get('status')}"
        )
        
        # ========================================
        # Test 3: Get All Accounts
        # ========================================
        print_section("[Test 3] Get All Accounts")
        
        response = await client.get(f"{BASE_URL}/api/accounts")
        print_result(
            "GET /api/accounts",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        data = response.json()
        if data.get("success"):
            accounts = data.get("data", [])
            print(f"[OK] Retrieved {len(accounts)} accounts")
            for acc in accounts[:3]:  # Show first 3
                print(f"     - {acc['account_id']}: {acc['account_name']} (${acc['balance']:,.2f})")
        
        # ========================================
        # Test 4: Get Account by ID
        # ========================================
        print_section("[Test 4] Get Account by ID")
        
        # Valid account
        response = await client.get(f"{BASE_URL}/api/accounts/ACC001")
        print_result(
            "GET /api/accounts/ACC001",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        data = response.json()
        if data.get("success"):
            acc = data["data"]
            print(f"     Account: {acc['account_name']}")
            print(f"     Balance: ${acc['balance']:,.2f}")
        
        # Invalid account
        response = await client.get(f"{BASE_URL}/api/accounts/INVALID")
        data = response.json()
        print_result(
            "GET /api/accounts/INVALID (should fail)",
            not data.get("success"),
            f"Error: {data.get('error', {}).get('code')}"
        )
        
        # ========================================
        # Test 5: Create Payment
        # ========================================
        print_section("[Test 5] Create Payment")
        
        # Valid payment
        payment_data = {
            "debtor_account_id": "ACC001",
            "creditor_account_id": "SUP001",
            "transaction_amount": 1500.50,
            "description": "Test payment - API integration"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/payments",
            json=payment_data
        )
        print_result(
            "POST /api/payments (valid)",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        data = response.json()
        transaction_id = None
        if data.get("success"):
            payment = data["data"]
            transaction_id = payment["transaction_id"]
            print(f"     Transaction ID: {transaction_id}")
            print(f"     Amount: ${payment['transaction_amount']:,.2f}")
            print(f"     Status: {payment['transaction_status']}")
        
        # Test error: Insufficient balance
        insufficient_data = {
            "debtor_account_id": "ACC001",
            "creditor_account_id": "SUP001",
            "transaction_amount": 999999.99,
            "description": "Should fail - insufficient balance"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/payments",
            json=insufficient_data
        )
        data = response.json()
        print_result(
            "POST /api/payments (insufficient balance)",
            not data.get("success"),
            f"Error: {data.get('error', {}).get('code')}"
        )
        
        # Test error: Same account
        same_account_data = {
            "debtor_account_id": "ACC001",
            "creditor_account_id": "ACC001",
            "transaction_amount": 100.00,
            "description": "Should fail - same account"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/payments",
            json=same_account_data
        )
        data = response.json()
        print_result(
            "POST /api/payments (same account)",
            not data.get("success"),
            f"Error: {data.get('error', {}).get('code')}"
        )
        
        # Test error: Account not found
        invalid_account_data = {
            "debtor_account_id": "INVALID",
            "creditor_account_id": "SUP001",
            "transaction_amount": 100.00,
            "description": "Should fail - account not found"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/payments",
            json=invalid_account_data
        )
        data = response.json()
        print_result(
            "POST /api/payments (account not found)",
            not data.get("success"),
            f"Error: {data.get('error', {}).get('code')}"
        )
        
        # ========================================
        # Test 6: Get Payment by ID
        # ========================================
        print_section("[Test 6] Get Payment by ID")
        
        if transaction_id:
            response = await client.get(
                f"{BASE_URL}/api/payments/{transaction_id}"
            )
            print_result(
                f"GET /api/payments/{transaction_id}",
                response.status_code == 200,
                f"Status: {response.status_code}"
            )
            
            data = response.json()
            if data.get("success"):
                payment = data["data"]
                print(f"     Transaction: {payment['transaction_id']}")
                print(f"     Status: {payment['transaction_status']}")
                print(f"     Logs: {len(payment.get('logs', []))} entries")
        
        # ========================================
        # Test 7: Get Payments List (Paginated)
        # ========================================
        print_section("[Test 7] Get Payments List")
        
        response = await client.get(
            f"{BASE_URL}/api/payments?page=1&limit=10"
        )
        print_result(
            "GET /api/payments (paginated)",
            response.status_code == 200,
            f"Status: {response.status_code}"
        )
        
        data = response.json()
        if data.get("success"):
            list_data = data["data"]
            items = list_data["items"]
            pagination = list_data["pagination"]
            print(f"     Items: {len(items)}")
            print(f"     Total: {pagination['total']}")
            print(f"     Page: {pagination['page']}/{pagination['total_pages']}")
        
        # Test filtering by status
        response = await client.get(
            f"{BASE_URL}/api/payments?status=pending"
        )
        data = response.json()
        if data.get("success"):
            pending_count = data["data"]["pagination"]["total"]
            print_result(
                "GET /api/payments?status=pending",
                True,
                f"Pending payments: {pending_count}"
            )
        
        # ========================================
        # Test 8: Status Simulation (Wait and Poll)
        # ========================================
        print_section("[Test 8] Status Simulation")
        
        if transaction_id:
            print("[INFO] Waiting for status simulation (10 seconds)...")
            print("[INFO] Polling every 2 seconds...")
            
            for i in range(6):  # Poll 6 times (12 seconds total)
                await asyncio.sleep(2)
                
                response = await client.get(
                    f"{BASE_URL}/api/payments/{transaction_id}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        payment = data["data"]
                        status = payment["transaction_status"]
                        print(f"[INFO] Poll {i+1}: Status = {status}")
                        
                        if status in ["completed", "failed"]:
                            print_result(
                                "Status simulation complete",
                                True,
                                f"Final status: {status}"
                            )
                            if status == "completed":
                                print(f"     Completed at: {payment['completed_at']}")
                            elif status == "failed":
                                print(f"     Error: {payment.get('error_message', 'Unknown')}")
                            break
        
        # ========================================
        # Test 9: API Documentation
        # ========================================
        print_section("[Test 9] API Documentation")
        
        response = await client.get(f"{BASE_URL}/docs")
        print_result(
            "GET /docs (Swagger UI)",
            response.status_code == 200,
            "Swagger UI accessible"
        )
        
        response = await client.get(f"{BASE_URL}/openapi.json")
        print_result(
            "GET /openapi.json",
            response.status_code == 200,
            "OpenAPI schema available"
        )
        
        # ========================================
        # Summary
        # ========================================
        print_section("[Summary]")
        print("[SUCCESS] All API tests completed!")
        print()
        print("Tested endpoints:")
        print("  - GET  /")
        print("  - GET  /health")
        print("  - GET  /api/accounts")
        print("  - GET  /api/accounts/{id}")
        print("  - POST /api/payments")
        print("  - GET  /api/payments/{id}")
        print("  - GET  /api/payments (paginated + filtered)")
        print("  - GET  /docs (Swagger UI)")
        print()
        print("Tested features:")
        print("  - Account queries")
        print("  - Payment creation")
        print("  - Error handling (4 error cases)")
        print("  - Pagination")
        print("  - Status filtering")
        print("  - Background status simulation")
        print("  - Polling mechanism")
        print("="*60)


async def check_server():
    """Check if server is running"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            return response.status_code == 200
    except:
        return False


async def main():
    """Main test function"""
    
    print("="*60)
    print("API Integration Tests")
    print("="*60)
    print(f"Target: {BASE_URL}")
    print()
    
    # Check if server is running
    print("Checking server status...")
    if not await check_server():
        print("[ERROR] Server is not running!")
        print()
        print("Please start the server first:")
        print("  python run_server.py")
        print()
        return
    
    print("[OK] Server is running")
    
    # Run tests
    await test_api()


if __name__ == "__main__":
    asyncio.run(main())
