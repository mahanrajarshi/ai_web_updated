from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import asyncio
import subprocess
import json


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# AI WebUI Models
class ScanRequest(BaseModel):
    model_name: str
    environment: str
    tool: str
    probe: str
    session_id: Optional[str] = None

class ScanSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str
    environment: str
    tool: str
    probe: str
    status: str = "pending"  # pending, running, completed, failed
    output: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

class ModelInfo(BaseModel):
    name: str
    tag: str
    size: str
    modified: str

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.session_connections: dict = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        if session_id not in self.session_connections:
            self.session_connections[session_id] = []
        self.session_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        self.active_connections.remove(websocket)
        if session_id in self.session_connections:
            if websocket in self.session_connections[session_id]:
                self.session_connections[session_id].remove(websocket)

    async def send_personal_message(self, message: str, session_id: str):
        if session_id in self.session_connections:
            for connection in self.session_connections[session_id]:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "AI WebUI API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# AI WebUI Endpoints
@api_router.get("/models")
async def get_models():
    """Get available Ollama models"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        
        models = []
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    models.append({
                        "name": parts[0],
                        "tag": parts[1] if len(parts) > 1 else "latest",
                        "size": parts[2] if len(parts) > 2 else "unknown",
                        "modified": " ".join(parts[3:]) if len(parts) > 3 else "unknown"
                    })
        
        return {"models": models}
    except subprocess.CalledProcessError:
        return {"models": [], "error": "Ollama not available"}
    except Exception as e:
        return {"models": [], "error": str(e)}

@api_router.get("/environments")
async def get_environments():
    """Get available conda environments"""
    try:
        result = subprocess.run(
            ["conda", "env", "list", "--json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        env_data = json.loads(result.stdout)
        environments = []
        
        for env_path in env_data.get("envs", []):
            env_name = os.path.basename(env_path)
            environments.append({
                "name": env_name,
                "path": env_path
            })
        
        return {"environments": environments}
    except subprocess.CalledProcessError:
        return {"environments": [], "error": "Conda not available"}
    except Exception as e:
        return {"environments": [], "error": str(e)}

@api_router.get("/garak/probes")
async def get_garak_probes():
    """Get available Garak probes"""
    # This is a predefined list based on the Garak documentation
    probes = [
        "test.Test",
        "dan.Dan_10_0",
        "dan.Dan_11_0", 
        "dan.Dan_6_2",
        "dan.Dan_7_0",
        "dan.Dan_8_0",
        "dan.Dan_9_0",
        "continuation.ContinueSlursReclaimedSlurs",
        "continuation.ContinueSlursReclaimedSlursPrefix",
        "promptinject.PromptInject",
        "realtoxicityprompts.RealToxicityPrompts",
        "malwaregen.Malwaregen",
        "xss.XSS",
        "latentinjection.LatentInjection",
        "encoding.InjectBase64",
        "encoding.InjectHex",
        "encoding.InjectROT13",
        "encoding.InjectUnicode",
        "exploitation.Exploitation"
    ]
    
    return {"probes": probes}

@api_router.post("/scan/start")
async def start_scan(scan_request: ScanRequest):
    """Start a vulnerability scan"""
    try:
        # Create scan session
        session = ScanSession(
            model_name=scan_request.model_name,
            environment=scan_request.environment,
            tool=scan_request.tool,
            probe=scan_request.probe,
            status="pending"
        )
        
        # Save session to database
        await db.scan_sessions.insert_one(session.dict())
        
        # Start scan asynchronously
        asyncio.create_task(run_scan(session))
        
        return {"session_id": session.id, "status": "started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/scan/{session_id}")
async def get_scan_status(session_id: str):
    """Get scan status and output"""
    try:
        session = await db.scan_sessions.find_one({"id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Remove MongoDB ObjectId to make it JSON serializable
        if "_id" in session:
            del session["_id"]
        
        return session
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_scan(session: ScanSession):
    """Run the actual vulnerability scan"""
    try:
        # Update status to running
        await db.scan_sessions.update_one(
            {"id": session.id},
            {"$set": {"status": "running"}}
        )
        
        # Send status update via WebSocket
        await manager.send_personal_message(
            json.dumps({"type": "status", "status": "running"}),
            session.id
        )
        
        # Build command based on tool
        if session.tool == "garak":
            command = [
                "conda", "run", "-n", session.environment,
                "python", "-m", "garak",
                "--model_type", "ollama",
                "--model_name", session.model_name,
                "--probes", session.probe
            ]
        else:
            raise ValueError(f"Unsupported tool: {session.tool}")
        
        # Send command info with full command
        command_str = " ".join(command)
        await manager.send_personal_message(
            json.dumps({
                "type": "command",
                "command": command_str
            }),
            session.id
        )
        
        # Send initial garak info
        await manager.send_personal_message(
            json.dumps({
                "type": "output",
                "line": f"garak LLM vulnerability scanner v0.12.0 ( https://github.com/NVIDIA/garak ) at {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}"
            }),
            session.id
        )
        
        # Create the process with unbuffered output
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            text=True,
            env={**os.environ, "PYTHONUNBUFFERED": "1"}  # Force unbuffered output
        )
        
        output_lines = []
        
        # Read output character by character to get real-time updates
        while True:
            try:
                # Read line by line but with timeout
                line_bytes = await asyncio.wait_for(process.stdout.readline(), timeout=1.0)
                if not line_bytes:
                    break
                    
                line = line_bytes.rstrip('\n\r')
                if line:
                    output_lines.append(line)
                    
                    # Send real-time output immediately
                    await manager.send_personal_message(
                        json.dumps({
                            "type": "output",
                            "line": line
                        }),
                        session.id
                    )
                    
                    # Also send any special formatting for progress bars
                    if "%" in line and ("|" in line or "█" in line):
                        await manager.send_personal_message(
                            json.dumps({
                                "type": "progress",
                                "line": line
                            }),
                            session.id
                        )
                        
            except asyncio.TimeoutError:
                # Check if process is still running
                if process.returncode is not None:
                    break
                continue
            except Exception as e:
                logger.error(f"Error reading output: {e}")
                break
        
        # Wait for process to complete
        await process.wait()
        
        # Update final status
        final_status = "completed" if process.returncode == 0 else "failed"
        final_output = "\n".join(output_lines)
        
        await db.scan_sessions.update_one(
            {"id": session.id},
            {
                "$set": {
                    "status": final_status,
                    "output": final_output,
                    "completed_at": datetime.utcnow()
                }
            }
        )
        
        # Send completion status
        await manager.send_personal_message(
            json.dumps({
                "type": "status",
                "status": final_status,
                "output": final_output
            }),
            session.id
        )
        
    except Exception as e:
        # Update error status
        await db.scan_sessions.update_one(
            {"id": session.id},
            {
                "$set": {
                    "status": "failed",
                    "output": str(e),
                    "completed_at": datetime.utcnow()
                }
            }
        )
        
        # Send error status
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "error": str(e)
            }),
            session.id
        )

# WebSocket endpoint for real-time updates
@app.websocket("/ws/terminal/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle any incoming WebSocket messages if needed
            pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
