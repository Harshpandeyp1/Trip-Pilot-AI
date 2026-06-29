import React, { useState, useEffect, useRef } from 'react';
import { 
  Compass, Plane, Wallet, Calendar, Shield, Package, Utensils, 
  Hotel, Car, Terminal, AlertTriangle, Download, RefreshCw, 
  Star, CheckCircle, Info, MapPin, Check, Globe, HelpCircle, 
  PhoneCall, ShieldAlert, Award
} from 'lucide-react';
import { 
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, 
  Tooltip, Cell, PieChart, Pie
} from 'recharts';

export default function App() {
  // Form State
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState('tokyo');
  const [budget, setBudget] = useState(1500);
  const [days, setDays] = useState(5);
  const [interests, setInterests] = useState(['Culture', 'Food']);
  const [hotelPref, setHotelPref] = useState('Boutique');
  const [foodPref, setFoodPref] = useState('Local');
  const [transportPref, setTransportPref] = useState('Public');
  const [nationality, setNationality] = useState('US');

  // App Execution State
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState([]);
  const [itinerary, setItinerary] = useState(null);
  const [activeTab, setActiveTab] = useState('itinerary'); // 'itinerary' | 'packing' | 'safety'
  const [exporting, setExporting] = useState(false);

  const terminalEndRef = useRef(null);

  // Load cities on mount
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/cities')
      .then(res => res.json())
      .then(data => {
        setCities(data);
        if (data.length > 0) {
          setSelectedCity(data[0].id);
        }
      })
      .catch(err => console.error("Error loading cities:", err));
  }, []);

  // Auto-scroll terminal logs
  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  // Handle interest toggling
  const handleInterestToggle = (interest) => {
    if (interests.includes(interest)) {
      setInterests(interests.filter(i => i !== interest));
    } else {
      setInterests([...interests, interest]);
    }
  };

  // Submit & Plan Itinerary
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setItinerary(null);
    setLogs([]);
    
    // 1. Establish SSE log stream connection
    const eventSource = new EventSource('http://127.0.0.1:8000/api/logs');
    
    eventSource.onmessage = (event) => {
      const logData = JSON.parse(event.data);
      if (logData.agent === 'System' && logData.message.includes('ended')) {
        eventSource.close();
      } else {
        setLogs((prevLogs) => [...prevLogs, logData]);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE stream error:", err);
      eventSource.close();
    };

    // 2. Fire planning HTTP request
    try {
      const response = await fetch('http://127.0.0.1:8000/api/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          destination: selectedCity,
          budget: parseFloat(budget),
          days: parseInt(days),
          interests,
          hotel_pref: hotelPref,
          food_pref: foodPref,
          transport_pref: transportPref,
          nationality
        })
      });
      
      if (!response.ok) {
        throw new Error(await response.text());
      }
      
      const data = await response.json();
      setItinerary(data);
      setActiveTab('itinerary');
    } catch (err) {
      console.error("Failed to generate plan:", err);
      setLogs(prev => [...prev, {
        agent: 'System',
        message: `Execution failed: ${err.message}`,
        type: 'error',
        timestamp: Date.now() / 1000
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Export Itinerary to Markdown
  const handleExport = async (format = 'markdown') => {
    if (!itinerary) return;
    setExporting(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          itinerary,
          format_type: format
        })
      });
      const data = await res.json();
      
      // Trigger file download
      const blob = new Blob([data.content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `TripPilot_Itinerary_${itinerary.destination}.${format === 'markdown' ? 'md' : 'html'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Export error:", err);
    } finally {
      setExporting(false);
    }
  };

  // Available Interests from JSON category mappings
  const availableInterests = ['Adventure', 'Culture', 'Food', 'Nature', 'Shopping', 'Relaxation'];

  // Formatting actual vs cap budget splits for Recharts
  const getExpenseChartData = () => {
    if (!itinerary) return [];
    const exp = itinerary.expenses;
    return [
      { name: 'Hotel', cost: exp.hotel_total_usd, fill: '#6366f1' },
      { name: 'Dining', cost: exp.dining_total_usd, fill: '#f43f5e' },
      { name: 'Attractions', cost: exp.attractions_total_usd, fill: '#10b981' },
      { name: 'Transport', cost: exp.transportation_total_usd, fill: '#eab308' },
      { name: 'Savings/Cont.', cost: exp.contingency_usd, fill: '#a855f7' }
    ];
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      
      {/* Top Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-600 text-white p-2.5 rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center">
            <Plane className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white bg-clip-text bg-gradient-to-r from-white via-slate-100 to-indigo-200">
                TripPilot AI
              </h1>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold uppercase tracking-wider flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                100% Offline
              </span>
            </div>
            <p className="text-xs text-slate-400">Offline Smart Travel Planner | Multi-Agent Orchestrator</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 text-xs text-slate-400 bg-slate-800/40 px-3 py-1.5 rounded-lg border border-slate-800">
            <Award className="w-4 h-4 text-amber-500" />
            <span>Kaggle agents Capstone Freestyle Entry</span>
          </div>
        </div>
      </header>

      {/* Main Grid Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Form & Agent Console (5 columns) */}
        <div className="lg:col-span-5 flex flex-col gap-6">
          
          {/* Trip Request Form */}
          <section className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 shadow-xl relative overflow-hidden backdrop-blur-sm">
            <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-full blur-2xl"></div>
            
            <h2 className="text-base font-semibold text-white flex items-center gap-2 mb-4">
              <Compass className="w-5 h-5 text-indigo-400" />
              Configure Travel Preferences
            </h2>

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              
              {/* Destination Dropdown */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">Destination</label>
                <select 
                  value={selectedCity} 
                  onChange={(e) => setSelectedCity(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                >
                  {cities.map(city => (
                    <option key={city.id} value={city.id}>{city.name} ({city.country})</option>
                  ))}
                  {cities.length === 0 && <option value="tokyo">Tokyo (Japan)</option>}
                </select>
              </div>

              {/* Budget & Days Rows */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">
                    Budget (USD): <span className="text-white font-semibold">${budget}</span>
                  </label>
                  <input 
                    type="range" 
                    min="300" 
                    max="5000" 
                    step="100"
                    value={budget} 
                    onChange={(e) => setBudget(e.target.value)}
                    className="w-full accent-indigo-500 h-1.5 bg-slate-950 rounded-lg appearance-none cursor-pointer"
                  />
                  <input 
                    type="number"
                    value={budget}
                    onChange={(e) => setBudget(e.target.value)}
                    className="w-full mt-2 bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1.5">
                    Duration: <span className="text-white font-semibold">{days} Days</span>
                  </label>
                  <input 
                    type="number" 
                    min="1" 
                    max="30"
                    value={days} 
                    onChange={(e) => setDays(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                </div>
              </div>

              {/* Preferences Accordion Style */}
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-[10px] font-medium text-slate-400 mb-1">Hotel Style</label>
                  <select 
                    value={hotelPref} 
                    onChange={(e) => setHotelPref(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2 py-1.5 text-xs text-slate-300 focus:outline-none"
                  >
                    <option value="Budget">Budget</option>
                    <option value="Boutique">Boutique</option>
                    <option value="Luxury">Luxury</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-medium text-slate-400 mb-1">Food style</label>
                  <select 
                    value={foodPref} 
                    onChange={(e) => setFoodPref(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2 py-1.5 text-xs text-slate-300 focus:outline-none"
                  >
                    <option value="Local">Local</option>
                    <option value="Vegetarian">Vegetarian</option>
                    <option value="Casual">Casual</option>
                    <option value="Fine Dining">Fine Dining</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-medium text-slate-400 mb-1">Transit</label>
                  <select 
                    value={transportPref} 
                    onChange={(e) => setTransportPref(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2 py-1.5 text-xs text-slate-300 focus:outline-none"
                  >
                    <option value="Public">Public</option>
                    <option value="Taxi">Taxi</option>
                    <option value="Rental">Rental</option>
                    <option value="Walking">Walking</option>
                  </select>
                </div>
              </div>

              {/* Nationality */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Citizen Nationality (Visa check)</label>
                <select 
                  value={nationality} 
                  onChange={(e) => setNationality(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none"
                >
                  <option value="US">United States (US)</option>
                  <option value="EU">European Union (EU)</option>
                  <option value="IN">India (IN)</option>
                  <option value="AU">Australia (AU)</option>
                  <option value="CA">Canada (CA)</option>
                </select>
              </div>

              {/* Interests Multi-Select */}
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-2">Travel Interests</label>
                <div className="flex flex-wrap gap-1.5">
                  {availableInterests.map(interest => {
                    const selected = interests.includes(interest);
                    return (
                      <button
                        type="button"
                        key={interest}
                        onClick={() => handleInterestToggle(interest)}
                        className={`text-xs px-3 py-1 rounded-full border transition-all ${
                          selected 
                            ? 'bg-indigo-600/20 text-indigo-400 border-indigo-500/40 font-medium' 
                            : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                        }`}
                      >
                        {interest}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || interests.length === 0}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm py-2.5 rounded-lg border border-indigo-500/30 transition-colors shadow-lg shadow-indigo-600/10 flex items-center justify-center gap-2 mt-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Executing ADK Agents...
                  </>
                ) : (
                  <>
                    <Compass className="w-4 h-4" />
                    Compile Trip Itinerary
                  </>
                )}
              </button>

            </form>
          </section>

          {/* Real-time Agent Log Console */}
          <section className="bg-slate-950 border border-slate-800/80 rounded-2xl flex-1 flex flex-col min-h-[300px] overflow-hidden shadow-2xl">
            
            {/* Console Header */}
            <div className="bg-slate-900 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-indigo-400 font-mono">
                <Terminal className="w-4 h-4" />
                <span>ADK_COLLABORATION_STREAM</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
                <span className="text-[10px] text-slate-500 font-mono uppercase">Live</span>
              </div>
            </div>

            {/* Scrollable logs box */}
            <div className="flex-1 p-4 font-mono text-[11px] overflow-y-auto max-h-[350px] flex flex-col gap-2.5 scrollbar-thin">
              {logs.length === 0 && (
                <div className="text-slate-600 italic text-center my-auto">
                  Terminal ready. Enter settings and click Generate to observe multi-agent collaboration...
                </div>
              )}
              {logs.map((log, index) => {
                let textClass = "text-slate-300";
                let agentBadgeClass = "bg-slate-800 text-slate-400";
                
                if (log.type === "system") {
                  textClass = "text-yellow-500/90 font-bold";
                  agentBadgeClass = "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20";
                } else if (log.type === "success") {
                  textClass = "text-emerald-400 font-medium";
                  agentBadgeClass = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                } else if (log.type === "tool_call") {
                  textClass = "text-indigo-300 italic";
                  agentBadgeClass = "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20";
                } else if (log.agent === "PlannerAgent") {
                  textClass = "text-white font-medium";
                  agentBadgeClass = "bg-slate-800 text-white font-semibold";
                }

                return (
                  <div key={index} className="flex flex-col gap-1 border-b border-slate-900/60 pb-1.5 last:border-b-0">
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-semibold ${agentBadgeClass}`}>
                        {log.agent}
                      </span>
                      <span className="text-[9px] text-slate-600">
                        {new Date(log.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </span>
                    </div>
                    
                    <p className={`pl-1 leading-relaxed ${textClass}`}>
                      {log.message}
                    </p>

                    {log.tool_call && (
                      <div className="mt-1 pl-3 border-l-2 border-indigo-500/40 bg-slate-900/40 p-1.5 rounded-r font-mono text-[10px] text-indigo-200">
                        <span className="text-indigo-400 font-bold">🛠️ CALL:</span> {log.tool_call}
                        {log.tool_result && (
                          <div className="mt-1 text-slate-400">
                            <span className="text-emerald-500 font-bold">↩️ RESULT:</span> {log.tool_result}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
              <div ref={terminalEndRef}></div>
            </div>
          </section>

        </div>

        {/* Right Column: Dashboard Welcome or Output (7 columns) */}
        <div className="lg:col-span-7 flex flex-col">
          
          {/* Welcome Screen (No Itinerary) */}
          {!itinerary && !loading && (
            <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-10 flex-1 flex flex-col items-center justify-center text-center shadow-inner relative overflow-hidden">
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-900/10 via-transparent to-transparent"></div>
              
              <div className="w-20 h-20 bg-indigo-950/80 border border-slate-800 text-indigo-400 p-5 rounded-3xl shadow-xl flex items-center justify-center mb-6 relative">
                <div className="absolute -inset-1 rounded-3xl bg-indigo-500/10 blur animate-pulse"></div>
                <Compass className="w-10 h-10" />
              </div>

              <h2 className="text-2xl font-bold text-white mb-3">Your Journey Starts Here</h2>
              <p className="text-sm text-slate-400 max-w-md mb-8 leading-relaxed">
                Configure your destination, duration, and constraints on the left. 
                Our multi-agent system will query offline databases via local MCP tools to build a custom travel plan.
              </p>

              {/* Architectural features callout */}
              <div className="grid grid-cols-2 gap-4 max-w-lg w-full">
                <div className="p-4 bg-slate-900/60 border border-slate-850 rounded-xl text-left">
                  <div className="text-xs text-indigo-400 font-semibold mb-1 flex items-center gap-1.5">
                    <Terminal className="w-3.5 h-3.5" /> Google ADK Orchestrator
                  </div>
                  <p className="text-[11px] text-slate-400">Sequentially delegates work to 8 specialists like BudgetAgent and SafetyAgent.</p>
                </div>

                <div className="p-4 bg-slate-900/60 border border-slate-850 rounded-xl text-left">
                  <div className="text-xs text-indigo-400 font-semibold mb-1 flex items-center gap-1.5">
                    <Globe className="w-3.5 h-3.5" /> Local MCP Tools
                  </div>
                  <p className="text-[11px] text-slate-400">Interacts with local datasets (hotels.json, visa.json) using standard MCP schemas.</p>
                </div>
              </div>
            </div>
          )}

          {/* Loader Layout while planning */}
          {loading && !itinerary && (
            <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-10 flex-1 flex flex-col items-center justify-center text-center shadow-inner relative overflow-hidden">
              <div className="w-16 h-16 border-4 border-indigo-600/30 border-t-indigo-500 rounded-full animate-spin mb-6"></div>
              <h3 className="text-lg font-semibold text-white mb-2">Orchestrating AI Agents...</h3>
              <p className="text-xs text-slate-400 max-w-xs leading-relaxed">
                Sub-agents are currently running budget splits, querying local hotels, and arranging itineraries over the local MCP.
              </p>
            </div>
          )}

          {/* Output Presentation (Itinerary is loaded) */}
          {itinerary && (
            <div className="flex-1 flex flex-col gap-6">
              
              {/* Trip Summary Dashboard Header */}
              <section className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl"></div>
                
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
                      <MapPin className="w-3.5 h-3.5 text-indigo-400" />
                      <span>{itinerary.destination}, {itinerary.country}</span>
                      <span className="mx-1.5">•</span>
                      <span>{itinerary.season} Season</span>
                    </div>
                    <h2 className="text-xl font-bold text-white mb-2">
                      {itinerary.summary.title}
                    </h2>
                    <p className="text-xs text-slate-400 leading-relaxed max-w-xl">
                      {itinerary.description}
                    </p>
                  </div>
                  
                  {/* Export Buttons */}
                  <div className="flex flex-row md:flex-col gap-2 shrink-0">
                    <button
                      onClick={() => handleExport('markdown')}
                      className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 border border-indigo-500/30 transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Export MD</span>
                    </button>
                    <button
                      onClick={() => handleExport('html')}
                      className="px-3 py-1.5 bg-slate-850 hover:bg-slate-800 text-slate-300 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 border border-slate-700 transition-colors"
                    >
                      <Globe className="w-3.5 h-3.5" />
                      <span>Export HTML</span>
                    </button>
                  </div>
                </div>

                {/* KPI stats bar */}
                <div className="grid grid-cols-3 gap-4 border-t border-slate-800/80 pt-4 mt-4">
                  <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-850">
                    <span className="block text-[10px] text-slate-500 font-medium uppercase">Budget status</span>
                    <span className={`text-xs font-bold capitalize ${
                      itinerary.summary.status === 'under_budget' ? 'text-emerald-400' : 'text-rose-400'
                    }`}>
                      {itinerary.summary.status.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-850">
                    <span className="block text-[10px] text-slate-500 font-medium uppercase">Estimated actual</span>
                    <span className="text-xs font-bold text-white">${itinerary.expenses.total_estimated_usd} USD</span>
                  </div>
                  <div className="bg-slate-950/50 p-2.5 rounded-lg border border-slate-850">
                    <span className="block text-[10px] text-slate-500 font-medium uppercase">Money remaining</span>
                    <span className="text-xs font-bold text-indigo-400">${itinerary.summary.savings_usd} USD</span>
                  </div>
                </div>
              </section>

              {/* Tab Navigation */}
              <div className="flex border-b border-slate-800">
                <button
                  onClick={() => setActiveTab('itinerary')}
                  className={`px-4 py-2 text-xs font-medium border-b-2 transition-all ${
                    activeTab === 'itinerary' 
                      ? 'border-indigo-500 text-white' 
                      : 'border-transparent text-slate-400 hover:text-slate-350'
                  }`}
                >
                  📍 Timeline Itinerary
                </button>
                <button
                  onClick={() => setActiveTab('packing')}
                  className={`px-4 py-2 text-xs font-medium border-b-2 transition-all ${
                    activeTab === 'packing' 
                      ? 'border-indigo-500 text-white' 
                      : 'border-transparent text-slate-400 hover:text-slate-350'
                  }`}
                >
                  🎒 Packing Checklist
                </button>
                <button
                  onClick={() => setActiveTab('safety')}
                  className={`px-4 py-2 text-xs font-medium border-b-2 transition-all ${
                    activeTab === 'safety' 
                      ? 'border-indigo-500 text-white' 
                      : 'border-transparent text-slate-400 hover:text-slate-350'
                  }`}
                >
                  🛡️ Customs & Safety
                </button>
              </div>

              {/* Tab Content Panels */}
              <div className="flex-1 flex flex-col gap-6">
                
                {/* Tab: Itinerary & Budget Breakdown */}
                {activeTab === 'itinerary' && (
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-6 flex-1">
                    
                    {/* Daily Timeline (7 columns) */}
                    <div className="md:col-span-7 flex flex-col gap-4">
                      {itinerary.itinerary.map((day) => (
                        <div 
                          key={day.day} 
                          className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 shadow-sm"
                        >
                          <div className="flex items-center justify-between border-b border-slate-800/50 pb-2 mb-3">
                            <span className="text-xs font-bold text-white flex items-center gap-1.5">
                              <Calendar className="w-4 h-4 text-indigo-400" />
                              Day {day.day}
                            </span>
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                              Est: ${day.cost_usd}
                            </span>
                          </div>

                          <div className="flex flex-col gap-3 relative before:absolute before:top-2 before:bottom-2 before:left-[11px] before:w-[2px] before:bg-slate-800">
                            {day.timeline.map((slot, sIdx) => {
                              let typeIcon = <HelpCircle className="w-3.5 h-3.5" />;
                              let colorClass = "text-indigo-400 bg-indigo-950/80 border-indigo-900";
                              
                              if (slot.type === "Meal") {
                                typeIcon = <Utensils className="w-3.5 h-3.5" />;
                                colorClass = "text-rose-400 bg-rose-950/80 border-rose-900";
                              } else if (slot.type === "Attraction") {
                                typeIcon = <MapPin className="w-3.5 h-3.5" />;
                                colorClass = "text-emerald-400 bg-emerald-950/80 border-emerald-905";
                              }

                              return (
                                <div key={sIdx} className="flex gap-4 items-start pl-1 relative z-10">
                                  <div className={`w-6 h-6 rounded-full border flex items-center justify-center shrink-0 ${colorClass}`}>
                                    {typeIcon}
                                  </div>
                                  <div>
                                    <div className="flex items-baseline gap-2">
                                      <span className="text-[9px] font-mono text-slate-500">{slot.time.split(' - ')[0]}</span>
                                      <h4 className="text-xs font-semibold text-white">{slot.name}</h4>
                                    </div>
                                    <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">{slot.description}</p>
                                    {slot.cost_usd > 0 && (
                                      <span className="inline-block text-[9px] text-slate-500 mt-1 bg-slate-950 px-1.5 py-0.5 rounded">
                                        Cost: ${slot.cost_usd}
                                      </span>
                                    )}
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Accommodation & Expenses Charts (5 columns) */}
                    <div className="md:col-span-5 flex flex-col gap-6">
                      
                      {/* Accommodation Card */}
                      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 flex flex-col gap-3 relative">
                        <h3 className="text-xs font-bold text-white flex items-center gap-1.5 border-b border-slate-800/50 pb-2">
                          <Hotel className="w-4 h-4 text-indigo-400" />
                          Hotel Accommodation
                        </h3>
                        <div>
                          <div className="flex items-center justify-between">
                            <h4 className="text-sm font-semibold text-white">{itinerary.hotel.name}</h4>
                            <span className="text-[10px] px-2 py-0.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-md font-semibold">
                              {itinerary.hotel.category}
                            </span>
                          </div>
                          
                          <div className="flex items-center gap-1 text-[11px] text-slate-500 mt-1">
                            <span className="flex items-center text-amber-500 gap-0.5 font-bold">
                              <Star className="w-3.5 h-3.5 fill-current" /> {itinerary.hotel.rating}
                            </span>
                            <span>•</span>
                            <span className="text-slate-400">${itinerary.hotel.price_per_night} / night</span>
                          </div>
                          
                          <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">
                            {itinerary.hotel.description}
                          </p>

                          <div className="flex flex-wrap gap-1.5 mt-3">
                            {itinerary.hotel.amenities.map(am => (
                              <span key={am} className="text-[9px] px-2 py-0.5 bg-slate-950 text-slate-500 rounded border border-slate-850">
                                {am}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Visualized Expenses Allocation Chart */}
                      <div className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-4 flex flex-col gap-3">
                        <h3 className="text-xs font-bold text-white flex items-center gap-1.5 border-b border-slate-800/50 pb-2">
                          <Wallet className="w-4 h-4 text-indigo-400" />
                          Actual Cost Allocation
                        </h3>
                        
                        <div className="h-44 w-full flex items-center justify-center">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={getExpenseChartData()} layout="vertical" margin={{ left: -10, right: 10, top: 0, bottom: 0 }}>
                              <XAxis type="number" stroke="#475569" fontSize={9} />
                              <YAxis dataKey="name" type="category" stroke="#475569" fontSize={9} width={80} />
                              <Tooltip cursor={{ fill: 'transparent' }} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: 10 }} />
                              <Bar dataKey="cost" radius={4}>
                                {getExpenseChartData().map((entry, index) => (
                                  <Cell key={`cell-${index}`} fill={entry.fill} />
                                ))}
                              </Bar>
                            </BarChart>
                          </ResponsiveContainer>
                        </div>

                        {/* Warnings if critical */}
                        {itinerary.expenses.total_estimated_usd > itinerary.budget && (
                          <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 text-[10px] text-rose-400 rounded-lg flex items-start gap-1.5">
                            <AlertTriangle className="w-4 h-4 shrink-0" />
                            <p>Warning: Estimated actual costs exceed your target budget. Consider switching to cheaper restaurants or a lower tier hotel.</p>
                          </div>
                        )}

                      </div>

                    </div>

                  </div>
                )}

                {/* Tab: Packing Checklist */}
                {activeTab === 'packing' && (
                  <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 shadow-xl">
                    <h3 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3 mb-4">
                      <Package className="w-5 h-5 text-indigo-400" />
                      Custom Packing Checklist ({itinerary.season} Travel)
                    </h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      
                      {/* Essentials */}
                      <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-850">
                        <h4 className="text-xs font-bold text-indigo-400 mb-3 uppercase tracking-wider flex items-center gap-1.5">
                          <CheckCircle className="w-4 h-4" /> Essentials
                        </h4>
                        <ul className="flex flex-col gap-2">
                          {itinerary.packing_list.essentials.map((item, idx) => (
                            <li key={idx} className="flex items-center gap-2 text-[11px] text-slate-300">
                              <input type="checkbox" className="rounded bg-slate-950 border-slate-800 text-indigo-600 focus:ring-0 focus:ring-offset-0 w-3.5 h-3.5" />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Clothing */}
                      <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-850">
                        <h4 className="text-xs font-bold text-rose-400 mb-3 uppercase tracking-wider flex items-center gap-1.5">
                          <CheckCircle className="w-4 h-4" /> Clothing
                        </h4>
                        <ul className="flex flex-col gap-2">
                          {itinerary.packing_list.clothing.map((item, idx) => (
                            <li key={idx} className="flex items-center gap-2 text-[11px] text-slate-300">
                              <input type="checkbox" className="rounded bg-slate-950 border-slate-800 text-indigo-600 focus:ring-0 focus:ring-offset-0 w-3.5 h-3.5" />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Activity specific */}
                      <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-850">
                        <h4 className="text-xs font-bold text-emerald-400 mb-3 uppercase tracking-wider flex items-center gap-1.5">
                          <CheckCircle className="w-4 h-4" /> Activity Gear
                        </h4>
                        <ul className="flex flex-col gap-2">
                          {itinerary.packing_list.activity_gear.length === 0 ? (
                            <li className="text-[11px] text-slate-550 italic">No specific activities items required.</li>
                          ) : (
                            itinerary.packing_list.activity_gear.map((item, idx) => (
                              <li key={idx} className="flex items-center gap-2 text-[11px] text-slate-300">
                                <input type="checkbox" className="rounded bg-slate-950 border-slate-800 text-indigo-600 focus:ring-0 focus:ring-offset-0 w-3.5 h-3.5" />
                                <span>{item}</span>
                              </li>
                            ))
                          )}
                        </ul>
                      </div>

                    </div>
                  </div>
                )}

                {/* Tab: Customs & Safety */}
                {activeTab === 'safety' && (
                  <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 shadow-xl flex flex-col gap-6">
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      
                      {/* Emergency Contacts */}
                      <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-850 flex flex-col gap-3">
                        <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5 border-b border-slate-800 pb-2">
                          <PhoneCall className="w-4 h-4" /> Emergency Phone Numbers
                        </h4>
                        <div className="grid grid-cols-3 gap-2 text-center text-xs">
                          <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                            <span className="block text-[9px] text-slate-500 font-medium">Police</span>
                            <span className="font-mono font-bold text-rose-400">{itinerary.safety_advice.emergency_contacts.police}</span>
                          </div>
                          <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                            <span className="block text-[9px] text-slate-500 font-medium">Fire/Ambulance</span>
                            <span className="font-mono font-bold text-rose-400">{itinerary.safety_advice.emergency_contacts.fire_ambulance}</span>
                          </div>
                          <div className="bg-slate-900 p-2.5 rounded border border-slate-800">
                            <span className="block text-[9px] text-slate-500 font-medium">Medical</span>
                            <span className="font-mono font-bold text-indigo-400">{itinerary.safety_advice.emergency_contacts.medical_helpline}</span>
                          </div>
                        </div>
                      </div>

                      {/* Visa guidelines */}
                      <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-850 flex flex-col gap-3">
                        <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5 border-b border-slate-800 pb-2">
                          <ShieldAlert className="w-4 h-4" /> Immigration Entry Check
                        </h4>
                        <div className="p-3 bg-indigo-950/30 border border-indigo-900/60 rounded text-[11px] text-indigo-300 leading-relaxed">
                          {itinerary.safety_advice.visa_guidelines}
                        </div>
                      </div>

                    </div>

                    {/* Local Customs & Useful Phrases */}
                    <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                      
                      {/* Local Customs (7 columns) */}
                      <div className="md:col-span-7 bg-slate-950/50 p-4 rounded-xl border border-slate-850 flex flex-col gap-3">
                        <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5 border-b border-slate-800 pb-2">
                          <Shield className="w-4 h-4" /> Cultural Norms & Etiquette
                        </h4>
                        <ul className="flex flex-col gap-2.5">
                          {itinerary.safety_advice.local_customs.map((custom, idx) => (
                            <li key={idx} className="flex gap-2 items-start text-[11px] text-slate-350 leading-relaxed">
                              <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0 mt-1.5"></span>
                              <span>{custom}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Phrases (5 columns) */}
                      <div className="md:col-span-5 bg-slate-950/50 p-4 rounded-xl border border-slate-850 flex flex-col gap-3">
                        <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5 border-b border-slate-800 pb-2">
                          <Globe className="w-4 h-4" /> Basic Offline Phrasebook
                        </h4>
                        <div className="flex flex-col gap-2">
                          {itinerary.safety_advice.useful_phrases.map((ph, idx) => (
                            <div key={idx} className="flex items-center justify-between bg-slate-900 p-2 rounded border border-slate-800/80">
                              <span className="text-[10px] text-slate-400 font-medium">{ph.english}</span>
                              <span className="text-[11px] text-indigo-300 font-semibold font-mono">{ph.local}</span>
                            </div>
                          ))}
                          {itinerary.safety_advice.useful_phrases.length === 0 && (
                            <span className="text-[11px] text-slate-550 italic">No translation required (English speaking).</span>
                          )}
                        </div>
                      </div>

                    </div>

                  </div>
                )}

              </div>

            </div>
          )}

        </div>

      </main>

      {/* Footer credits */}
      <footer className="border-t border-slate-900/60 bg-slate-950/50 px-6 py-4 flex flex-col md:flex-row items-center justify-between text-[10px] text-slate-500 gap-4 mt-6">
        <p>© 2026 TripPilot AI travel assistant. Built with Google ADK framework and Model Context Protocol.</p>
        <div className="flex gap-4">
          <span>Offline Database Verified</span>
          <span>•</span>
          <span>Zero External Calls</span>
        </div>
      </footer>

    </div>
  );
}
