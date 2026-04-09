import React from 'react';
import {
  View, Text, ScrollView, StyleSheet,
} from 'react-native';
import Svg, { Circle as SvgCircle, Text as SvgText } from 'react-native-svg';

import { COLORS, SPACING, RADIUS, scoreColor, scoreLabel } from '../utils/theme';
import { useAnalysis } from '../utils/AnalysisContext';
import Badge from '../components/Badge';
import Card from '../components/Card';

const INCIDENT_ICONS = {
  Accident:   '🚗',
  'Road Works': '🚧',
  Flooding:   '🌊',
  Jam:        '🔴',
  default:    '⚠',
};

function CongestionRing({ score }) {
  const color = scoreColor(score);
  const radius = 44;
  const circumference = 2 * Math.PI * radius;
  const filled = (score / 100) * circumference;
  const dashOffset = circumference - filled;

  return (
    <Svg width={110} height={110} viewBox="0 0 110 110">
      <SvgCircle cx={55} cy={55} r={radius} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={10} />
      <SvgCircle
        cx={55} cy={55} r={radius} fill="none" stroke={color} strokeWidth={10}
        strokeDasharray={`${circumference}`}
        strokeDashoffset={dashOffset}
        strokeLinecap="round"
        rotation={-90} originX={55} originY={55}
        opacity={0.9}
      />
      <SvgText x={55} y={50} textAnchor="middle" fill={color} fontSize={22} fontWeight="800">
        {score.toFixed(1)}
      </SvgText>
      <SvgText x={55} y={66} textAnchor="middle" fill="rgba(255,255,255,0.3)" fontSize={10}>
        {scoreLabel(score)}
      </SvgText>
    </Svg>
  );
}

function SpeedBar({ label, speed, max = 60, color }) {
  const pct = Math.min((speed / max) * 100, 100);
  return (
    <View style={styles.speedRow}>
      <Text style={styles.speedLabel}>{label}</Text>
      <View style={styles.speedTrack}>
        <View style={[styles.speedFill, { width: `${pct}%`, backgroundColor: color }]} />
      </View>
      <Text style={[styles.speedVal, { color }]}>{speed} km/h</Text>
    </View>
  );
}

// Placeholder data when no API result yet
const PLACEHOLDER = {
  location: 'Koramangala',
  time: '18:00',
  weather: 'rain',
  congestion: 'medium',
  congestion_score: 93.6,
  avg_speed: 12,
  free_flow_speed: 55,
  traffic_volume: 'very high',
  incident_count: 3,
  incident_types: ['Accident', 'Road Works'],
  roadwork_active: true,
  confidence: 'high',
  trend: 'worsening',
  trend_delta: 78.2,
};

export default function OutputScreen() {
  const { result, params } = useAnalysis();
  const data = result ?? PLACEHOLDER;

  const badgeVariant = data.congestion_score >= 80 ? 'red' : data.congestion_score >= 60 ? 'orange' : data.congestion_score >= 40 ? 'amber' : 'green';
  const trendVariant = data.trend === 'worsening' ? 'red' : data.trend === 'moderate' ? 'amber' : 'green';

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>

      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Analysis Output</Text>
          <Text style={styles.meta}>{data.location} • {data.time ?? 'LIVE'} • {data.weather} • {data.confidence} confidence</Text>
        </View>
        <Badge label="LIVE" variant="green" dot />
      </View>

      {/* Congestion ring + detail */}
      <Card>
        <Text style={styles.sectionLabel}>Congestion Overview</Text>
        <View style={styles.ringRow}>
          <CongestionRing score={data.congestion_score} />
          <View style={styles.ringDetails}>
            {[
              ['Avg Speed',    `${data.avg_speed} km/h`,    data.avg_speed < 20 ? COLORS.warn : COLORS.text],
              ['Free Flow',   `${data.free_flow_speed} km/h`, COLORS.text],
              ['Volume',       data.traffic_volume,           data.traffic_volume === 'very high' ? COLORS.danger : COLORS.text],
              ['Trend',        `${data.trend?.toUpperCase()} ↑`, data.trend === 'worsening' ? COLORS.danger : COLORS.text],
              ['Delta',        `+${data.trend_delta?.toFixed(1)}%`, COLORS.danger],
            ].map(([k, v, c]) => (
              <View key={k} style={styles.detailRow}>
                <Text style={styles.detailKey}>{k}</Text>
                <Text style={[styles.detailVal, { color: c }]}>{v}</Text>
              </View>
            ))}
          </View>
        </View>
      </Card>

      {/* Speed breakdown */}
      <Card>
        <Text style={styles.sectionLabel}>Speed Breakdown</Text>
        <SpeedBar label="Current"  speed={data.avg_speed}         max={60} color={COLORS.danger} />
        <SpeedBar label="Free Flow" speed={data.free_flow_speed}  max={60} color={COLORS.accent} />
        <SpeedBar label="T+5 min"  speed={Math.max(data.avg_speed - 3, 5)} max={60} color={COLORS.accent2} />
        <SpeedBar label="T+10 min" speed={Math.max(data.avg_speed - 5, 4)} max={60} color={COLORS.warn} />
      </Card>

      {/* Incidents */}
      {data.incident_count > 0 && (
        <Card>
          <Text style={styles.sectionLabel}>Active Incidents ({data.incident_count})</Text>
          <View style={{ gap: 8 }}>
            {(data.incident_types || []).map((type, i) => (
              <View key={i} style={styles.incidentRow}>
                <Text style={{ fontSize: 18 }}>{INCIDENT_ICONS[type] || INCIDENT_ICONS.default}</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.incidentName}>{type}</Text>
                  <Text style={styles.incidentSub}>Detected within 2km radius</Text>
                </View>
                <Badge label={`${(0.4 + i * 0.7).toFixed(1)} km`} variant={i === 0 ? 'red' : 'amber'} />
              </View>
            ))}
            {data.roadwork_active && (
              <View style={styles.incidentRow}>
                <Text style={{ fontSize: 18 }}>🚧</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.incidentName}>Road Works Active</Text>
                  <Text style={styles.incidentSub}>Capacity reduction on route</Text>
                </View>
                <Badge label="ACTIVE" variant="amber" />
              </View>
            )}
          </View>
        </Card>
      )}

      {/* Property grid */}
      <View style={styles.propGrid}>
        {[
          ['Confidence',    data.confidence?.toUpperCase(),     'green'],
          ['Roadwork',      data.roadwork_active ? 'YES' : 'NO', data.roadwork_active ? 'amber' : 'green'],
          ['EV Chargers',   '3 nearby',                          'blue'],
          ['Priority Veh.', 'ACTIVE',                            'blue'],
        ].map(([k, v, variant]) => (
          <Card key={k} style={styles.propCard}>
            <Text style={styles.propKey}>{k}</Text>
            <Text style={[styles.propVal, { color: variant === 'green' ? COLORS.accent : variant === 'amber' ? COLORS.warn : COLORS.accent3 }]}>{v}</Text>
          </Card>
        ))}
      </View>

    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: COLORS.bg },
  content: { padding: SPACING.lg, gap: SPACING.md, paddingBottom: 40 },

  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  title: { fontSize: 18, fontWeight: '800', color: COLORS.text },
  meta: { fontSize: 10, color: COLORS.muted, marginTop: 2 },
  sectionLabel: { fontSize: 10, fontWeight: '700', color: COLORS.muted, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 },

  ringRow: { flexDirection: 'row', alignItems: 'center', gap: 20 },
  ringDetails: { flex: 1, gap: 7 },
  detailRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  detailKey: { fontSize: 12, color: COLORS.muted },
  detailVal: { fontSize: 12, fontWeight: '700' },

  speedRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 8 },
  speedLabel: { fontSize: 11, color: COLORS.muted, width: 75 },
  speedTrack: { flex: 1, height: 6, backgroundColor: COLORS.bg3, borderRadius: 3, overflow: 'hidden' },
  speedFill: { height: '100%', borderRadius: 3 },
  speedVal: { fontSize: 11, fontWeight: '700', width: 55, textAlign: 'right' },

  incidentRow: { flexDirection: 'row', alignItems: 'center', gap: 10, padding: SPACING.md, backgroundColor: COLORS.bg3, borderRadius: RADIUS.sm, borderWidth: 0.5, borderColor: COLORS.border },
  incidentName: { fontSize: 12, fontWeight: '600', color: COLORS.text },
  incidentSub: { fontSize: 10, color: COLORS.muted },

  propGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  propCard: { width: '48%', gap: 4 },
  propKey: { fontSize: 10, color: COLORS.muted, textTransform: 'uppercase', letterSpacing: 0.8 },
  propVal: { fontSize: 14, fontWeight: '800' },
});
