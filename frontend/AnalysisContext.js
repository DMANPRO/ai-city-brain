import React, { createContext, useContext, useState } from 'react';

const AnalysisContext = createContext(null);

export function AnalysisProvider({ children }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [params, setParams] = useState({
    location: 'Koramangala',
    time: null,       // null = live
    weather: 'clear',
    simulation: 0,    // T+0, T+5, T+10, T+15
  });

  return (
    <AnalysisContext.Provider value={{ result, setResult, loading, setLoading, params, setParams }}>
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  return useContext(AnalysisContext);
}
