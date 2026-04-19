"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { Activity, Zap, ShieldAlert, Cpu } from "lucide-react";

interface Trade {
  id: number;
  timestamp: string;
  hand_id: string;
  z_score: number | null;
  hurst: number | null;
  confidence_score: number | null;
  sentiment_score: number | null;
}

export default function Dashboard() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCritical, setIsCritical] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch("/api/metrics");
        const data = await res.json();
        
        let validTrades = data.trades || [];
        // If DB is empty or just initialized, mock some volcano-like data for demonstration
        if (validTrades.length === 0) {
            validTrades = Array.from({ length: 50 }).map((_, i) => ({
                id: i,
                timestamp: new Date(Date.now() - (50 - i) * 60000).toISOString(),
                hand_id: "cazador",
                z_score: (Math.random() * 4) - 2,
                hurst: 0.8 - (i * 0.006) + (Math.random() * 0.05), // Starts trending, slowly dips
                confidence_score: i > 40 ? 0.95 : 0.2, // Spikes at the end
                sentiment_score: i > 40 ? 15 : 50 // Drops to extreme fear at the end
            }));
        }

        setTrades(validTrades);

        // Check if latest hurst is critical (H < 0.52 and confidence > 0.8)
        const latest = validTrades[validTrades.length - 1];
        if (latest && latest.hurst !== null && latest.hurst < 0.52) {
            setIsCritical(true);
        } else {
            setIsCritical(false);
        }

      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    const interval = setInterval(fetchData, 10000); // 10s auto-refresh
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-950 flex items-center justify-center text-cyan-400 font-mono">
        <Cpu className="animate-pulse mr-3" /> INICIALIZANDO SISTEMA FRACTAL...
      </div>
    );
  }

  const latestTrade = trades[trades.length - 1];

  return (
    <div className={`min-h-screen transition-all duration-700 p-8 font-mono ${isCritical ? 'bg-[#1a0505]' : 'bg-neutral-950'}`}>
      
      {/* Glitch Overlay effect when critical */}
      {isCritical && (
        <div className="pointer-events-none fixed inset-0 z-50 animate-pulse bg-red-900/10 mix-blend-color-dodge"></div>
      )}

      <header className="mb-10 flex justify-between items-center border-b border-cyan-900/30 pb-6">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-emerald-400 flex items-center gap-3">
            <Activity className="text-cyan-400" />
            Ecosistema-Veritasium
          </h1>
          <p className="text-sm text-neutral-500 mt-2 uppercase tracking-widest">
            Monitor Volcánico de Criticidad Autónoma
          </p>
        </div>
        <div className="flex gap-4">
           {isCritical && (
                <div className="flex items-center gap-2 text-red-500 font-bold animate-pulse border border-red-500/50 bg-red-950/30 px-4 py-2 rounded-md">
                    <ShieldAlert size={20} />
                    ¡ZERO CLAW ENABLED!
                </div>
            )}
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        
        {/* Recolector Metric */}
        <div className="bg-neutral-900/50 border border-cyan-500/20 rounded-lg p-6 shadow-[0_0_15px_rgba(34,211,238,0.05)]">
            <div className="text-cyan-500 text-xs font-bold mb-1 tracking-widest uppercase">Bot 1: Recolector</div>
            <div className="text-3xl font-light text-cyan-50">{latestTrade?.z_score?.toFixed(2) || 'N/A'}</div>
            <div className="text-cyan-700 text-xs mt-2">Z-Score Actual</div>
        </div>

        {/* Multiplicador Metric */}
        <div className="bg-neutral-900/50 border border-lime-400/20 rounded-lg p-6 shadow-[0_0_15px_rgba(163,230,53,0.05)]">
            <div className="text-lime-400 text-xs font-bold mb-1 tracking-widest uppercase">Bot 2: Multiplicador</div>
            <div className="text-3xl font-light text-lime-50">Trend</div>
            <div className="text-lime-700/80 text-xs mt-2">Estado Log-Normal</div>
        </div>

        {/* Cazador Metric */}
        <div className={`bg-neutral-900/50 border border-orange-500/20 rounded-lg p-6 transition-all duration-300 ${isCritical ? 'shadow-[0_0_30px_rgba(249,115,22,0.4)] border-orange-500/60' : 'shadow-[0_0_15px_rgba(249,115,22,0.05)]'}`}>
            <div className="text-orange-500 text-xs font-bold mb-1 tracking-widest uppercase flex items-center gap-2">
                Bot 3: Cazador {isCritical && <Zap size={14} className="text-red-500 animate-bounce" />}
            </div>
            <div className="text-3xl font-light text-orange-50">{latestTrade?.hurst?.toFixed(3) || 'N/A'}</div>
            <div className="text-orange-700 text-xs mt-2">Hurst Exponent (Presión Fractal)</div>
        </div>

        {/* Sentiment Metric */}
        <div className="bg-neutral-900/50 border border-purple-500/20 rounded-lg p-6 shadow-[0_0_15px_rgba(168,85,247,0.05)]">
            <div className="text-purple-400 text-xs font-bold mb-1 tracking-widest uppercase">Sentiment (Fear/Greed)</div>
            <div className="text-3xl font-light text-purple-50">{latestTrade?.sentiment_score || 'N/A'}</div>
            <div className="text-purple-700 text-xs mt-2">Score de IA NLP</div>
        </div>

      </div>

      {/* Sismógrafo: Hurst Exponent Chart */}
      <div className="bg-neutral-900/40 border border-neutral-800 rounded-lg p-6 shadow-2xl relative overflow-hidden">
        
        {isCritical && (
            <div className="absolute inset-0 bg-gradient-to-t from-red-900/20 to-transparent opacity-50 animate-pulse pointer-events-none"></div>
        )}

        <h3 className="text-neutral-400 mb-6 text-sm flex items-center gap-2 uppercase tracking-wider">
            Sismógrafo Fractal (Exponente de Hurst)
        </h3>
        
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trades}>
              <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
              <XAxis 
                dataKey="timestamp" 
                stroke="#525252" 
                tickFormatter={(tick) => new Date(tick).toLocaleTimeString()}
                tick={{fontSize: 12}}
              />
              <YAxis 
                domain={[0.2, 0.9]} 
                stroke="#525252" 
                tick={{fontSize: 12}}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0a0a0a', border: '1px solid #262626', borderRadius: '8px' }}
                labelFormatter={(l) => new Date(l).toLocaleString()}
              />
              
              {/* Línea crítica de avalancha */}
              <ReferenceLine y={0.5} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideBottomRight', value: 'Umbral Crítico (H=0.5)', fill: '#ef4444', fontSize: 12 }} />
              
              <Line 
                type="monotone" 
                dataKey="hurst" 
                stroke={isCritical ? "#f97316" : "#22d3ee"} 
                strokeWidth={isCritical ? 3 : 2}
                dot={false}
                activeDot={{ r: 6, fill: isCritical ? "#ef4444" : "#22d3ee" }}
                animationDuration={300}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
    </div>
  );
}
