import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def run_all_tests():
    print("=" * 60)
    print("RUNNING OMNIPULSE API INTEGRATION TESTS")
    print("=" * 60)

    endpoints = [
        ("/health", "Health Check"),
        ("/api/overview", "Executive Overview KPIs"),
        ("/api/sales/monthly", "Monthly Revenue Trend"),
        ("/api/sales/categories?limit=5", "Top Categories"),
        ("/api/sales/top-products?limit=5", "Top Products"),
        ("/api/sales/payments", "Payment Breakdown"),
        ("/api/customers/segments", "Customer RFM Segments"),
        ("/api/customers/geography", "Geographic Distribution"),
        ("/api/inventory/summary", "Inventory Summary"),
        ("/api/inventory/alerts?limit=5", "Inventory Alerts"),
        ("/api/inventory/items?limit=5", "Inventory Items"),
        ("/api/logistics/summary", "Logistics Delivery Summary"),
        ("/api/logistics/by-state", "Logistics by State"),
        ("/api/geography/map-data", "Geospatial State Map Data"),
        ("/api/reviews/summary", "Review Analytics"),
        ("/api/ai-insights", "AI Operational Insights"),
        ("/api/export/inventory-alerts", "Export Inventory Alerts CSV"),
        ("/api/export/customer-segments", "Export Customer Segments CSV"),
        ("/api/export/state-logistics", "Export State Logistics CSV"),
    ]

    all_passed = True
    for path, name in endpoints:
        t0 = time.time()
        try:
            resp = client.get(path)
            duration = round((time.time() - t0) * 1000, 1)
            if resp.status_code == 200:
                data = resp.json() if "application/json" in resp.headers.get("content-type", "") else resp.text
                sample_info = f"items={len(data)}" if isinstance(data, list) else f"bytes={len(data)}"
                print(f"[PASS] {name:<32} | {duration:>6}ms | {path} ({sample_info})")
            else:
                print(f"[FAIL] {name:<32} | Status: {resp.status_code} | {resp.text}")
                all_passed = False
        except Exception as e:
            print(f"[ERROR] {name:<32} | {str(e)}")
            all_passed = False

    # POST Endpoints Testing
    post_endpoints = [
        ("/api/ai-chat", "AI Chat Assistant", {"query": "What is our current revenue?"}),
        ("/api/simulator/project", "Scenario Simulator", {
            "delivery_delay_reduction_days": 2.0,
            "churn_winback_rate": 10.0,
            "stockout_prevention_rate": 50.0,
            "freight_subsidy_pct": 5.0
        })
    ]

    for path, name, payload in post_endpoints:
        t0 = time.time()
        try:
            resp = client.post(path, json=payload)
            duration = round((time.time() - t0) * 1000, 1)
            if resp.status_code == 200:
                print(f"[PASS] {name:<32} | {duration:>6}ms | {path} (keys={len(resp.json())})")
            else:
                print(f"[FAIL] {name:<32} | Status: {resp.status_code} | {resp.text}")
                all_passed = False
        except Exception as e:
            print(f"[ERROR] {name:<32} | {str(e)}")
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("ALL ENDPOINT TESTS PASSED SUCCESSFULLY!")
    else:
        print("SOME TESTS FAILED.")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
