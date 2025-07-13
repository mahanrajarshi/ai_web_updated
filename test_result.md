#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

## user_problem_statement: Clone and develop an AI WebUI application for security testing of Large Language Models using industry-standard tools Garak and PromptMap. The application should include:

### Core Features Required:
- 4-Step Wizard Interface for guided vulnerability testing
- Real-time Terminal Output via WebSocket connections
- Dual Tool Support: Garak and PromptMap integration
- Model Management: Automatic Ollama model detection and selection
- Environment Management: Conda environment integration
- Report Generation: HTML (Garak) and JSON (PromptMap) report downloads
- Session Management: Track and resume vulnerability scans

### UI/UX Features:
- Modern Glassmorphism UI with gradient backgrounds
- Responsive Design for desktop and mobile devices
- Step-by-step Wizard with visual progress indicators
- Error Handling with user-friendly messages
- Loading States and animations for better UX

### Security Testing Capabilities:
- 34+ Garak Probe Categories including test.Test, dan, continuation, promptinject, realtoxicityprompts, malwaregen, xss, latentinjection, encoding, exploitation
- PromptMap Integration for automated prompt injection testing
- Real-time Scan Monitoring with live terminal output
- Comprehensive Reporting with detailed vulnerability analysis

### Prerequisites:
- Ollama for LLM model management
- Miniconda/Anaconda for Python environment management
- Node.js (v16+) and Python (3.8+)

## Current Status:
- ✅ Basic FastAPI backend with MongoDB integration
- ✅ React frontend with basic landing page
- ✅ Environment setup complete
- ✅ Services running properly
- ✅ AI WebUI backend endpoints implemented and tested

## backend:
  - task: "Basic FastAPI setup with MongoDB"
    implemented: true
    working: true
    file: "server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
        - agent: "main"
        - comment: "Basic FastAPI server with CORS, MongoDB connection, and status check endpoints working"

  - task: "AI WebUI API endpoints for vulnerability scanning"
    implemented: true
    working: true
    file: "server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
        - agent: "main"
        - comment: "Implemented /api/models, /api/environments, /api/garak/probes, /api/scan/start, /api/scan/{session_id}, and WebSocket /ws/terminal/{session_id} endpoints"

  - task: "WebSocket real-time terminal output"
    implemented: true
    working: true
    file: "server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
        - agent: "main"
        - comment: "WebSocket endpoint for real-time scan output implemented with connection manager"

## frontend:
  - task: "Basic React setup with landing page"
    implemented: true
    working: true
    file: "App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
        - agent: "main"
        - comment: "Basic React app with routing, Tailwind CSS, and API integration working"

  - task: "4-Step Wizard Interface"
    implemented: true
    working: true
    file: "App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
        - agent: "main"
        - comment: "Complete 4-step wizard interface implemented with glassmorphism UI, step indicators, and proper navigation"

  - task: "Model Management UI"
    implemented: true
    working: true
    file: "App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
        - agent: "main"
        - comment: "Step 1 model selection UI implemented with proper error handling for missing Ollama models"

  - task: "Environment Selection UI"
    implemented: true
    working: true
    file: "App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
        - agent: "main"
        - comment: "Step 2 environment selection UI implemented with conda environment detection"

  - task: "Tool and Probe Selection UI"
    implemented: true
    working: true
    file: "App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
        - agent: "main"
        - comment: "Step 3 tool and probe selection UI implemented with Garak probe list"

  - task: "Vulnerability Scan Interface"
    implemented: true
    working: true
    file: "App.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: true
        - agent: "main"
        - comment: "Step 4 vulnerability scan interface implemented with real-time terminal output and WebSocket connection"

## metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

## test_plan:
  current_focus:
    - "Frontend AI WebUI implementation"
    - "4-Step Wizard Interface"
    - "Real-time terminal integration"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

## agent_communication:
    - agent: "main"
    - message: "Initial setup complete. Repository cloned and basic template running. Ready to implement AI WebUI features for LLM security testing."
    - agent: "testing"
    - message: "Completed comprehensive testing of all AI WebUI backend endpoints. All 7 endpoints tested successfully: API health, models, environments, garak probes, scan start, scan status, and WebSocket terminal. Fixed ObjectId serialization issue in scan status endpoint. Backend API structure is solid and ready for frontend integration."