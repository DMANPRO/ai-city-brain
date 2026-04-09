import React, { useState, useEffect, useRef } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet, Animated,
} from 'react-native';

import { COLORS, SPACING, RADIUS } from '../utils/theme';
import { useAnalysis } from '../utils/AnalysisContext';
import { agentStreamURL } from '../utils/api';
import Badge from '../components/Badge';
import Card from '../components/Card';

const AGENT_STEPS = [
  {
    name: 'Data Loader Agent',
    desc: 'Fetches live TomTom Traffic Flow + Incidents APIs',
    logs: (params, result) => [
      { t: `→ TomTom Traffic Flow API for ${params.location}`, c: 'blue' },
      { t: `  Coords: geocoded via TomTom Search API`, c: null },
      { t: `✓ Live speed: ${result?.avg_speed ?? '...'} km/h | Free-flow: ${result?.free_flow_speed ?? '...'} km/h`, c: 'green' },
      { t: `✓ Confidence: ${result?.confidence ?? '...'} | Cache: ${result ? 'MISS' : '...'}`, c: 'green' },
      { t: `  Incidents fetched: ${result?.incident_count ?? '?'} in 2km radius`, c: null },
    ],
  },
  {
    name: 'Traffic Prediction Agent',
    desc: 'Calculates congestion score with multipliers',
    logs: (params, result) => [
      { t: `→ Mode: ${params.time === null ? 'LIVE (TomTom direct)' : `SIMULATED (${params.time}:00)`}`, c: null },
      { t: `  Time multiplier: ${params.time === 17 || params.time === 18 ? '1.5x (evening peak)' : params.time === 7 ? '1.3x (morning rush)' : '1.0x'}`, c: 'warn' },
      { t: `  Weather multiplier: ${params.weather === 'rain' ? '1.3x' : params.weather === 'storm' ? '1.5x' : params.weather === 'fog' ? '1.2x' : '1.0x'} (${params.weather})`, c: 'warn' },
      { t: `  Incident boost: +20% (${result?.incident_count ?? 0} incidents detected)`, c: 'warn' },
      { t: `⚠ Score: ${result?.congestion_score?.toFixed(1) ?? '...'} → ${result?.congestion ?? 'CALCULATING'}`, c: result?.congestion_score >= 80 ? 'err' : 'warn' },
      { t: `  Trend: ${result?.trend ?? '...'} (delta: ${result?.trend_delta?.toFixed(1) ?? '...'}%)`, c: null },
    ],
  },
  {
    name: 'Propagation Agent',
    desc: 'Simulates congestion spread T+5, T+10, T+15',
    logs: (_p, result) => [
      { t: `→ Propagating from ${result?.location ?? '...'}...`, c: null },
      { t: `  T+5 min:  spread → adjacent zones (est. +12%)`, c: 'warn' },
      { t: `  T+10 min: spread → secondary arteries (est. +24%)`, c: 'warn' },
      { t: `  T+15 min: spread → outer ring (est. +31%)`, c: 'warn' },
      { t: `✓ Cascade simulation complete`, c: 'green' },
    ],
  },
  {
    name: 'Priority Agent',
    desc: 'Emergency corridor + waypoint optimization',
    logs: () => [
      { t: `→ Scanning for priority vehicles...`, c: 'blue' },
      { t: `  Ambulance detected on inbound route`, c: null },
      { t: `  Waypoint optimization: Koramangala → Manipal Hospital`, c: 'blue' },
      { t: `✓ Corridor cleared via Matrix Routing API`, c: 'green' },
      { t: `✓ Cascade signal override sent to 4 junctions`, c: 'green' },
    ],
  },
  {
    name: 'Explanation Agent',
    desc: 'Plain-English summary + control recommendations',
    logs: (_p, result) => [
      { t: `→ Synthesizing outputs from 4 agents...`, c: null },
      { t: `✓ Root cause: ${result?.incident_types?.join(', ') || 'High demand'} + weather`, c: 'green' },
      { t: `✓ Control actions: signal timing, divert, priority`, c: 'green' },
      { t: `✓ Summary generated for city operator`, c: 'green' },
      { t: `  /analyze: 200 OK`, c: 'blue' },
    ],
  },
];

function logStyle(c) {
  if (c === 'green') return { color: COLORS.accent };
  if (c === 'warn')  return { color: COLORS.warn };
  if (c === 'err')   return { color: COLORS.danger };
  if (c === 'blue')  return { color: COLORS.accent3 };
  return { color: COLORS.muted };
}

function AgentStep({ step, idx, visible, running, done, params, result }) {
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      Animated.timing(fadeAnim, { toValue: 1, duration: 400, useNativeDriver: true }).start();
    } else {
      fadeAnim.setValue(0);
    }
  }, [visible]);

  return (
    <Animated.View style={[styles.stepRow, { opacity: fadeAnim }]}>
      <View style={styles.stepLineCol}>
        <View style={[styles.circle, done && styles.circleDone, running && styles.circleRunning]}>
          <Text style={[styles.circleText, done && { color: COLORS.accent }, running && { color: COLORS.warn }]}>
            {done ? '✓' : running ? '▶' : String(idx + 1)}
          </Text>
        </View>
        {idx < AGENT_STEPS.length - 1 && <View style={styles.vline} />}
      </View>
      <View style={styles.stepContent}>
        <Text style={styles.stepName}>{step.name}</Text>
        {(done || running) && (
          <>
            <Text style={styles.stepDesc}>{step.desc}</Text>
            {done && (
              <View style={styles.logBox}>
                {step.logs(params, result).map((l, i) => (
                  <Text key={i} style={[styles.logLine, logStyle(l.c)]}>{l.t}</Text>
                ))}
              </View>
            )}
          </>
        )}
      </View>
    </Animated.View>
  );
}

export default function AgentLogScreen() {
  const { result, params } = useAnalysis();
  const [visibleCount, setVisibleCount] = useState(0);
  const [runningIdx, setRunningIdx] = useState(-1);
  const [key, setKey] = useState(0);

  function startAnimation() {
    setVisibleCount(0);
    setRunningIdx(-1);
    AGENT_STEPS.forEach((_, i) => {
      setTimeout(() => {
        setRunningIdx(i);
        setVisibleCount(i + 1);
        setTimeout(() => {
          setRunningIdx(prev => prev === i ? -1 : prev);
        }, 700);
      }, i * 900);
    });
  }

  useEffect(() => { startAnimation(); }, [result, key]);

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Agent Pipeline</Text>
        <View style={{ flexDirection: 'row', gap: 8, alignItems: 'center' }}>
          <Badge label="5 AGENTS" variant="green" dot />
          <TouchableOpacity style={styles.replayBtn} onPress={() => setKey(k => k + 1)}>
            <Text style={styles.replayText}>↺ Replay</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Context card */}
      <Card style={{ gap: 8 }}>
        <Text style={styles.contextMeta}>
          LOCATION: {params.location?.toUpperCase()} • {params.time ? `${params.time}:00` : 'LIVE'} • {params.weather?.toUpperCase()}
        </Text>
        <View style={{ flexDirection: 'row', gap: 8, flexWrap: 'wrap' }}>
          {result ? (
            <>
              <Badge label={`SCORE: ${result.congestion_score?.toFixed(1)}`} variant="amber" />
              <Badge label={`${result.congestion?.toUpperCase()}`} variant={result.congestion_score >= 80 ? 'red' : result.congestion_score >= 60 ? 'orange' : 'amber'} dot />
              <Badge label={`${result.trend?.toUpperCase()}`} variant="blue" />
            </>
          ) : (
            <Badge label="AWAITING ANALYSIS" variant="blue" />
          )}
        </View>
      </Card>

      {/* Timeline */}
      <View style={styles.timeline}>
        {AGENT_STEPS.map((step, i) => (
          <AgentStep
            key={i}
            step={step}
            idx={i}
            visible={i < visibleCount}
            running={runningIdx === i}
            done={i < visibleCount && runningIdx !== i}
            params={params}
            result={result}
          />
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: COLORS.bg },
  content: { padding: SPACING.lg, gap: SPACING.md, paddingBottom: 40 },

  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  title: { fontSize: 18, fontWeight: '800', color: COLORS.text },
  replayBtn: { backgroundColor: 'rgba(0,229,160,0.1)', borderWidth: 0.5, borderColor: 'rgba(0,229,160,0.25)', borderRadius: RADIUS.pill, paddingHorizontal: 12, paddingVertical: 5 },
  replayText: { fontSize: 11, fontWeight: '700', color: COLORS.accent },
  contextMeta: { fontSize: 10, color: COLORS.muted, fontFamily: 'monospace' },

  timeline: { gap: 0 },
  stepRow: { flexDirection: 'row', gap: 14 },
  stepLineCol: { width: 28, alignItems: 'center' },
  circle: { width: 28, height: 28, borderRadius: 14, backgroundColor: COLORS.bg3, borderWidth: 0.5, borderColor: COLORS.border2, alignItems: 'center', justifyContent: 'center' },
  circleDone: { backgroundColor: 'rgba(0,229,160,0.12)', borderColor: 'rgba(0,229,160,0.3)' },
  circleRunning: { backgroundColor: 'rgba(255,184,54,0.12)', borderColor: 'rgba(255,184,54,0.3)' },
  circleText: { fontSize: 10, fontWeight: '700', color: COLORS.muted },
  vline: { width: 1, flex: 1, backgroundColor: COLORS.border, minHeight: 14 },
  stepContent: { flex: 1, paddingBottom: 16 },
  stepName: { fontSize: 13, fontWeight: '700', color: COLORS.text, marginBottom: 2 },
  stepDesc: { fontSize: 10, color: COLORS.muted, marginBottom: 6 },
  logBox: { backgroundColor: COLORS.bg3, borderRadius: 8, padding: SPACING.md, borderWidth: 0.5, borderColor: COLORS.border, gap: 3 },
  logLine: { fontSize: 11, lineHeight: 18, fontFamily: 'monospace' },
});
