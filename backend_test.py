#!/usr/bin/env python3
"""
Backend API Testing Script for AI WebUI Vulnerability Scanning Application
Tests all the new AI WebUI endpoints that were implemented.
"""

import requests
import json
import time
import asyncio
import websockets
import sys
from datetime import datetime

# Get backend URL from frontend env
BACKEND_URL = "https://67505abf-582c-44c9-95d6-d142dcdf6d47.preview.emergentagent.com/api"

class AIWebUITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if response_data and not success:
            print(f"   Response: {response_data}")
    
    def test_basic_api_health(self):
        """Test basic API health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "AI WebUI API":
                    self.log_test("Basic API Health", True, "API root endpoint working correctly", data)
                    return True
                else:
                    self.log_test("Basic API Health", False, f"Unexpected response: {data}", data)
                    return False
            else:
                self.log_test("Basic API Health", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Basic API Health", False, f"Connection error: {str(e)}")
            return False
    
    def test_get_models(self):
        """Test GET /api/models endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/models")
            if response.status_code == 200:
                data = response.json()
                if "models" in data:
                    models = data["models"]
                    if isinstance(models, list):
                        self.log_test("GET /api/models", True, f"Retrieved {len(models)} models", data)
                        return True
                    else:
                        self.log_test("GET /api/models", False, "Models field is not a list", data)
                        return False
                else:
                    self.log_test("GET /api/models", False, "Missing 'models' field in response", data)
                    return False
            else:
                self.log_test("GET /api/models", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("GET /api/models", False, f"Request error: {str(e)}")
            return False
    
    def test_get_environments(self):
        """Test GET /api/environments endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/environments")
            if response.status_code == 200:
                data = response.json()
                if "environments" in data:
                    environments = data["environments"]
                    if isinstance(environments, list):
                        self.log_test("GET /api/environments", True, f"Retrieved {len(environments)} environments", data)
                        return True
                    else:
                        self.log_test("GET /api/environments", False, "Environments field is not a list", data)
                        return False
                else:
                    self.log_test("GET /api/environments", False, "Missing 'environments' field in response", data)
                    return False
            else:
                self.log_test("GET /api/environments", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("GET /api/environments", False, f"Request error: {str(e)}")
            return False
    
    def test_get_garak_probes(self):
        """Test GET /api/garak/probes endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/garak/probes")
            if response.status_code == 200:
                data = response.json()
                if "probes" in data:
                    probes = data["probes"]
                    if isinstance(probes, list) and len(probes) > 0:
                        # Check if test.Test probe is available as mentioned in the request
                        if "test.Test" in probes:
                            self.log_test("GET /api/garak/probes", True, f"Retrieved {len(probes)} probes including test.Test", data)
                            return True
                        else:
                            self.log_test("GET /api/garak/probes", False, "test.Test probe not found in list", data)
                            return False
                    else:
                        self.log_test("GET /api/garak/probes", False, "Probes field is empty or not a list", data)
                        return False
                else:
                    self.log_test("GET /api/garak/probes", False, "Missing 'probes' field in response", data)
                    return False
            else:
                self.log_test("GET /api/garak/probes", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("GET /api/garak/probes", False, f"Request error: {str(e)}")
            return False
    
    def test_start_scan(self):
        """Test POST /api/scan/start endpoint"""
        try:
            # Use test data as specified in the request
            scan_data = {
                "model_name": "llama3:latest",
                "environment": "garak",
                "tool": "garak",
                "probe": "test.Test"
            }
            
            response = self.session.post(
                f"{self.base_url}/scan/start",
                json=scan_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "session_id" in data and "status" in data:
                    session_id = data["session_id"]
                    if data["status"] == "started":
                        self.log_test("POST /api/scan/start", True, f"Scan started with session_id: {session_id}", data)
                        return session_id
                    else:
                        self.log_test("POST /api/scan/start", False, f"Unexpected status: {data['status']}", data)
                        return None
                else:
                    self.log_test("POST /api/scan/start", False, "Missing session_id or status in response", data)
                    return None
            else:
                self.log_test("POST /api/scan/start", False, f"HTTP {response.status_code}", response.text)
                return None
        except Exception as e:
            self.log_test("POST /api/scan/start", False, f"Request error: {str(e)}")
            return None
    
    def test_get_scan_status(self, session_id):
        """Test GET /api/scan/{session_id} endpoint"""
        if not session_id:
            self.log_test("GET /api/scan/{session_id}", False, "No session_id provided")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/scan/{session_id}")
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "model_name", "environment", "tool", "probe", "status"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test("GET /api/scan/{session_id}", True, f"Retrieved scan status: {data['status']}", data)
                    return True
                else:
                    self.log_test("GET /api/scan/{session_id}", False, f"Missing fields: {missing_fields}", data)
                    return False
            elif response.status_code == 404:
                self.log_test("GET /api/scan/{session_id}", False, "Session not found (404)", response.text)
                return False
            else:
                self.log_test("GET /api/scan/{session_id}", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("GET /api/scan/{session_id}", False, f"Request error: {str(e)}")
            return False
    
    async def test_websocket_terminal(self, session_id):
        """Test WebSocket /ws/terminal/{session_id} endpoint"""
        if not session_id:
            self.log_test("WebSocket /ws/terminal/{session_id}", False, "No session_id provided")
            return False
            
        try:
            # Convert HTTPS URL to WSS for WebSocket
            ws_url = self.base_url.replace("https://", "wss://").replace("/api", "") + f"/ws/terminal/{session_id}"
            
            # Use connect with proper timeout handling
            async with websockets.connect(ws_url) as websocket:
                # Try to receive a message within 5 seconds
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    self.log_test("WebSocket /ws/terminal/{session_id}", True, f"WebSocket connected and received: {data['type'] if 'type' in data else 'message'}")
                    return True
                except asyncio.TimeoutError:
                    # No message received, but connection was successful
                    self.log_test("WebSocket /ws/terminal/{session_id}", True, "WebSocket connected successfully (no immediate messages)")
                    return True
                    
        except Exception as e:
            self.log_test("WebSocket /ws/terminal/{session_id}", False, f"WebSocket error: {str(e)}")
            return False
    
    def run_websocket_test(self, session_id):
        """Run WebSocket test in asyncio event loop"""
        try:
            return asyncio.run(self.test_websocket_terminal(session_id))
        except Exception as e:
            self.log_test("WebSocket /ws/terminal/{session_id}", False, f"Asyncio error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 60)
        print("AI WebUI Backend API Testing")
        print("=" * 60)
        print(f"Testing backend at: {self.base_url}")
        print()
        
        # Test 1: Basic API health
        if not self.test_basic_api_health():
            print("❌ Basic API health check failed. Stopping tests.")
            return False
        
        # Test 2: GET /api/models
        self.test_get_models()
        
        # Test 3: GET /api/environments
        self.test_get_environments()
        
        # Test 4: GET /api/garak/probes
        self.test_get_garak_probes()
        
        # Test 5: POST /api/scan/start
        session_id = self.test_start_scan()
        
        # Test 6: GET /api/scan/{session_id}
        if session_id:
            # Wait a moment for the scan to initialize
            time.sleep(2)
            self.test_get_scan_status(session_id)
            
            # Test 7: WebSocket /ws/terminal/{session_id}
            self.run_websocket_test(session_id)
        else:
            self.log_test("GET /api/scan/{session_id}", False, "Skipped due to failed scan start")
            self.log_test("WebSocket /ws/terminal/{session_id}", False, "Skipped due to failed scan start")
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All tests passed!")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            print("\nFailed tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
            return False

def main():
    """Main function to run tests"""
    tester = AIWebUITester()
    success = tester.run_all_tests()
    
    # Save detailed results to file
    with open("/app/backend_test_results.json", "w") as f:
        json.dump(tester.test_results, f, indent=2)
    
    print(f"\nDetailed results saved to: /app/backend_test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())