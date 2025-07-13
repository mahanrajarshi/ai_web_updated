import React, { useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Wizard Component
const VulnerabilityWizard = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [wizardData, setWizardData] = useState({
    model: null,
    environment: null,
    tool: 'garak',
    probe: null,
    sessionId: null
  });
  
  const [models, setModels] = useState([]);
  const [environments, setEnvironments] = useState([]);
  const [probes, setProbes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [scanOutput, setScanOutput] = useState([]);
  const [scanStatus, setScanStatus] = useState('idle');
  const [websocket, setWebsocket] = useState(null);

  // Fetch models on component mount
  useEffect(() => {
    fetchModels();
    fetchEnvironments();
    fetchProbes();
  }, []);

  const fetchModels = async () => {
    try {
      const response = await axios.get(`${API}/models`);
      setModels(response.data.models || []);
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const fetchEnvironments = async () => {
    try {
      const response = await axios.get(`${API}/environments`);
      setEnvironments(response.data.environments || []);
    } catch (error) {
      console.error('Error fetching environments:', error);
    }
  };

  const fetchProbes = async () => {
    try {
      const response = await axios.get(`${API}/garak/probes`);
      setProbes(response.data.probes || []);
    } catch (error) {
      console.error('Error fetching probes:', error);
    }
  };

  const nextStep = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const startScan = async () => {
    setLoading(true);
    try {
      const scanRequest = {
        model_name: wizardData.model,
        environment: wizardData.environment,
        tool: wizardData.tool,
        probe: wizardData.probe
      };

      const response = await axios.post(`${API}/scan/start`, scanRequest);
      const sessionId = response.data.session_id;
      
      setWizardData(prev => ({ ...prev, sessionId }));
      setScanStatus('running');
      
      // Connect to WebSocket for real-time output
      const wsUrl = `${BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://')}/ws/terminal/${sessionId}`;
      const ws = new WebSocket(wsUrl);
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'output') {
          setScanOutput(prev => [...prev, data.line]);
        } else if (data.type === 'status') {
          setScanStatus(data.status);
        } else if (data.type === 'command') {
          setScanOutput(prev => [...prev, `Starting Garak scan... Command: ${data.command}`]);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket connection closed');
      };

      setWebsocket(ws);
      
    } catch (error) {
      console.error('Error starting scan:', error);
      setScanStatus('failed');
    } finally {
      setLoading(false);
    }
  };

  const newScan = () => {
    setCurrentStep(1);
    setWizardData({
      model: null,
      environment: null,
      tool: 'garak',
      probe: null,
      sessionId: null
    });
    setScanOutput([]);
    setScanStatus('idle');
    if (websocket) {
      websocket.close();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">AI WebUI</h1>
          <p className="text-blue-200">LLM Security Testing Platform</p>
        </div>

        {/* Step Indicator */}
        <div className="flex justify-center mb-8">
          <div className="flex space-x-8">
            {[1, 2, 3, 4].map((step) => (
              <div key={step} className="flex items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                  step <= currentStep 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-600 text-gray-400'
                }`}>
                  {step}
                </div>
                {step < 4 && (
                  <div className={`w-16 h-1 ${
                    step < currentStep ? 'bg-blue-500' : 'bg-gray-600'
                  }`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-black bg-opacity-30 backdrop-blur-sm rounded-lg p-6 border border-gray-600">
          {/* Step 1: Model Selection */}
          {currentStep === 1 && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Step 1: Select Model</h2>
              <div className="space-y-4">
                {models.length > 0 ? (
                  models.map((model) => (
                    <div
                      key={model.name}
                      className={`p-4 rounded-lg border cursor-pointer transition-all ${
                        wizardData.model === model.name
                          ? 'border-blue-500 bg-blue-500 bg-opacity-20'
                          : 'border-gray-600 bg-gray-800 bg-opacity-50 hover:border-blue-400'
                      }`}
                      onClick={() => setWizardData(prev => ({ ...prev, model: model.name }))}
                    >
                      <div className="text-white font-medium">{model.name}</div>
                      <div className="text-gray-400 text-sm">Size: {model.size}</div>
                    </div>
                  ))
                ) : (
                  <div className="text-gray-400 text-center py-8">
                    <p>No models available. Please install Ollama models first.</p>
                  </div>
                )}
              </div>
              <div className="flex justify-end mt-6">
                <button
                  onClick={nextStep}
                  disabled={!wizardData.model}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Environment Selection */}
          {currentStep === 2 && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Step 2: Select Environment</h2>
              <div className="space-y-4">
                {environments.length > 0 ? (
                  environments.map((env) => (
                    <div
                      key={env.name}
                      className={`p-4 rounded-lg border cursor-pointer transition-all ${
                        wizardData.environment === env.name
                          ? 'border-blue-500 bg-blue-500 bg-opacity-20'
                          : 'border-gray-600 bg-gray-800 bg-opacity-50 hover:border-blue-400'
                      }`}
                      onClick={() => setWizardData(prev => ({ ...prev, environment: env.name }))}
                    >
                      <div className="text-white font-medium">{env.name}</div>
                      <div className="text-gray-400 text-sm">{env.path}</div>
                    </div>
                  ))
                ) : (
                  <div className="text-gray-400 text-center py-8">
                    <p>No environments available. Please set up conda environments first.</p>
                  </div>
                )}
              </div>
              <div className="flex justify-between mt-6">
                <button
                  onClick={prevStep}
                  className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                >
                  Previous
                </button>
                <button
                  onClick={nextStep}
                  disabled={!wizardData.environment}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Tool and Probe Selection */}
          {currentStep === 3 && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Step 3: Select Tool & Probe</h2>
              
              {/* Tool Selection */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-white mb-3">Tool</h3>
                <div className="space-y-2">
                  <div
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      wizardData.tool === 'garak'
                        ? 'border-blue-500 bg-blue-500 bg-opacity-20'
                        : 'border-gray-600 bg-gray-800 bg-opacity-50 hover:border-blue-400'
                    }`}
                    onClick={() => setWizardData(prev => ({ ...prev, tool: 'garak' }))}
                  >
                    <div className="text-white font-medium">Garak</div>
                    <div className="text-gray-400 text-sm">LLM vulnerability scanner</div>
                  </div>
                </div>
              </div>

              {/* Probe Selection */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-white mb-3">Probe</h3>
                <div className="max-h-60 overflow-y-auto space-y-2">
                  {probes.map((probe) => (
                    <div
                      key={probe}
                      className={`p-3 rounded-lg border cursor-pointer transition-all ${
                        wizardData.probe === probe
                          ? 'border-blue-500 bg-blue-500 bg-opacity-20'
                          : 'border-gray-600 bg-gray-800 bg-opacity-50 hover:border-blue-400'
                      }`}
                      onClick={() => setWizardData(prev => ({ ...prev, probe }))}
                    >
                      <div className="text-white text-sm">{probe}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-between mt-6">
                <button
                  onClick={prevStep}
                  className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                >
                  Previous
                </button>
                <button
                  onClick={nextStep}
                  disabled={!wizardData.probe}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Vulnerability Scan */}
          {currentStep === 4 && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">Step 4: Vulnerability Scan in Progress</h2>
              
              {/* Scan Configuration */}
              <div className="grid grid-cols-2 gap-4 mb-6 p-4 bg-gray-800 bg-opacity-50 rounded-lg">
                <div>
                  <span className="text-gray-400">Model:</span>
                  <span className="text-white ml-2">{wizardData.model}</span>
                </div>
                <div>
                  <span className="text-gray-400">Environment:</span>
                  <span className="text-white ml-2">{wizardData.environment}</span>
                </div>
                <div>
                  <span className="text-gray-400">Tool:</span>
                  <span className="text-white ml-2">{wizardData.tool}</span>
                </div>
                <div>
                  <span className="text-gray-400">Probe:</span>
                  <span className="text-white ml-2">{wizardData.probe}</span>
                </div>
              </div>

              {/* Terminal Output */}
              <div className="bg-black rounded-lg p-4 mb-6 min-h-96 max-h-96 overflow-y-auto">
                <div className="font-mono text-sm text-green-400">
                  {scanOutput.map((line, index) => (
                    <div key={index} className="mb-1">{line}</div>
                  ))}
                  {scanStatus === 'running' && (
                    <div className="flex items-center text-yellow-400">
                      <span className="mr-2">)</span>
                      <span className="animate-pulse">Scanning...</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-between">
                <button
                  onClick={prevStep}
                  disabled={scanStatus === 'running'}
                  className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <div className="space-x-4">
                  {scanStatus === 'idle' && (
                    <button
                      onClick={startScan}
                      disabled={loading}
                      className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? 'Starting...' : 'Start Scan'}
                    </button>
                  )}
                  {(scanStatus === 'completed' || scanStatus === 'failed') && (
                    <button
                      onClick={newScan}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      New Scan
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const Home = () => {
  return <VulnerabilityWizard />;
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}>
            <Route index element={<Home />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
