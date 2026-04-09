import React, { useState, useEffect, useRef } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  StyleSheet, ScrollView, Platform,
} from 'react-native';
import MapView, { Marker, Circle, Polyline, PROVIDER_GOOGLE } from 'react-native-maps';
import * as Location from 'expo-location';

import { COLORS, SPACING, RADIUS, scoreColor } from '../utils/theme';
import { fetchHotspots } from '../utils/api';

// Bengaluru city center
const BENGALURU = { latitude: 12.9716, longitude: 77.5946 };
const DELTA = { latitudeDelta: 0.18, longitudeDelta: 0.18 };

const MOCK_HOTSPOTS = [
  { name: 'Silk Board',     latitude: 12.9175, longitude: 77.6229, score: 93.6, trend: 'WORSENING' },
  { name: 'Marathahalli',   latitude: 12.9591, longitude: 77.6972, score: 78.2, trend: 'MODERATE' },
  { name: 'Indiranagar',    latitude: 12.9784, longitude: 77.6408, score: 61.0, trend: 'STABLE' },
  { name: 'Electronic City',latitude: 12.8399, longitude: 77.6770, score: 55.4, trend: 'MODERATE' },
  { name: 'Whitefield',     latitude: 12.9698, longitude: 77.7500, score: 48.2, trend: 'STABLE' },
  { name: 'Bannerghatta',   latitude: 12.8903, longitude: 77.5975, score: 24.0, trend: 'CLEAR' },
];

// Priority corridor waypoints (Koramangala → Manipal Hospital)
const PRIORITY_ROUTE = [
  { latitude: 12.9352, longitude: 77.6245 },
  { latitude: 12.9380, longitude: 77.6310 },
  { latitude: 12.9410, longitude: 77.6190 },
  { latitude: 12.9310, longitude: 77.6060 },
];

function trendIcon(trend) {
  if (trend === 'WORSENING') return '↑';
  if (trend === 'MODERATE')  return '→';
  if (trend === 'CLEAR')     return '✓';
  return '—';
}

export default function MapScreen() {
  const mapRef = useRef(null);
  const [hotspots, setHotspots] = useState(MOCK_HOTSPOTS);
  const [selected, setSelected] = useState(null);
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchHotspots();
        if (data?.length) setHotspots(data);
      } catch (_) {
        // use mock data above if API not reachable
      }
    })();
  }, []);

  function focusHotspot(h) {
    setSelected(h);
    mapRef.current?.animateToRegion({
      latitude: h.latitude, longitude: h.longitude,
      latitudeDelta: 0.04, longitudeDelta: 0.04,
    }, 600);
  }

  // Heat circle radius scales with score
  function heatRadius(score) { return score * 30; }

  return (
    <View style={styles.screen}>
      {/* Map */}
      <MapView
        ref={mapRef}
        style={StyleSheet.absoluteFillObject}
        provider={PROVIDER_GOOGLE}
        customMapStyle={DARK_MAP_STYLE}
        initialRegion={{ ...BENGALURU, ...DELTA }}
        showsUserLocation
        showsMyLocationButton={false}
      >
        {/* Heatmap circles */}
        {hotspots.map((h, i) => (
          <React.Fragment key={i}>
            <Circle
              center={{ latitude: h.latitude, longitude: h.longitude }}
              radius={heatRadius(h.score)}
              fillColor={scoreColor(h.score) + '30'}
              strokeColor={scoreColor(h.score) + '60'}
              strokeWidth={1}
            />
            <Circle
              center={{ latitude: h.latitude, longitude: h.longitude }}
              radius={heatRadius(h.score) * 0.45}
              fillColor={scoreColor(h.score) + '55'}
              strokeWidth={0}
            />
            <Marker
              coordinate={{ latitude: h.latitude, longitude: h.longitude }}
              onPress={() => focusHotspot(h)}
            >
              <View style={[styles.pin, { borderColor: scoreColor(h.score) }]}>
                <View style={[styles.pinDot, { backgroundColor: scoreColor(h.score) }]} />
              </View>
            </Marker>
          </React.Fragment>
        ))}

        {/* Priority ambulance corridor */}
        <Polyline
          coordinates={PRIORITY_ROUTE}
          strokeColor={COLORS.accent3}
          strokeWidth={3}
          lineDashPattern={[8, 5]}
        />
      </MapView>

      {/* Top search bar */}
      <View style={styles.topOverlay}>
        <TextInput
          style={styles.mapSearch}
          placeholder="Search location on map..."
          placeholderTextColor={COLORS.muted}
          value={searchText}
          onChangeText={setSearchText}
        />
        <View style={styles.legend}>
          {[['#ff4757','Critical'],['#ff6b35','High'],['#ffb836','Medium'],['#00e5a0','Low']].map(([c,l]) => (
            <View key={l} style={styles.legendRow}>
              <View style={[styles.legendDot, { backgroundColor: c }]} />
              <Text style={styles.legendText}>{l}</Text>
            </View>
          ))}
          <View style={styles.legendRow}>
            <View style={[styles.legendDot, { backgroundColor: COLORS.accent3 }]} />
            <Text style={styles.legendText}>Priority</Text>
          </View>
        </View>
      </View>

      {/* Bottom hotspot cards */}
      <View style={styles.bottomOverlay}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 10, paddingHorizontal: SPACING.lg }}>
          {hotspots.map((h, i) => (
            <TouchableOpacity key={i} style={[styles.hotspotCard, selected?.name === h.name && { borderColor: scoreColor(h.score) }]} onPress={() => focusHotspot(h)}>
              <Text style={styles.hotspotName}>{h.name}</Text>
              <Text style={[styles.hotspotScore, { color: scoreColor(h.score) }]}>{h.score.toFixed(1)}</Text>
              <Text style={styles.hotspotTrend}>{trendIcon(h.trend)} {h.trend}</Text>
            </TouchableOpacity>
          ))}
          <View style={[styles.hotspotCard, { borderColor: COLORS.accent3 }]}>
            <Text style={styles.hotspotName}>Priority Route</Text>
            <Text style={[styles.hotspotScore, { color: COLORS.accent3 }]}>ACTIVE</Text>
            <Text style={styles.hotspotTrend}>🚑 Ambulance</Text>
          </View>
        </ScrollView>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: COLORS.bg },

  topOverlay: {
    position: 'absolute', top: 16, left: 12, right: 12,
    flexDirection: 'row', gap: 8, alignItems: 'flex-start',
  },
  mapSearch: {
    flex: 1, backgroundColor: 'rgba(17,20,27,0.92)',
    borderWidth: 0.5, borderColor: COLORS.border2, borderRadius: RADIUS.md,
    color: COLORS.text, fontSize: 12, padding: SPACING.md,
  },
  legend: {
    backgroundColor: 'rgba(17,20,27,0.92)',
    borderWidth: 0.5, borderColor: COLORS.border2,
    borderRadius: RADIUS.md, padding: SPACING.sm, gap: 5,
  },
  legendRow: { flexDirection: 'row', alignItems: 'center', gap: 5 },
  legendDot: { width: 7, height: 7, borderRadius: 4 },
  legendText: { fontSize: 9, color: COLORS.muted },

  pin: { width: 18, height: 18, borderRadius: 9, borderWidth: 1.5, alignItems: 'center', justifyContent: 'center', backgroundColor: 'transparent' },
  pinDot: { width: 7, height: 7, borderRadius: 4 },

  bottomOverlay: {
    position: 'absolute', bottom: 0, left: 0, right: 0,
    paddingVertical: SPACING.lg,
    backgroundColor: 'linear-gradient(transparent, rgba(10,12,16,0.95))',
  },
  hotspotCard: {
    backgroundColor: 'rgba(17,20,27,0.95)',
    borderWidth: 0.5, borderColor: COLORS.border2,
    borderRadius: RADIUS.md, padding: SPACING.md,
    width: 140,
  },
  hotspotName: { fontSize: 11, fontWeight: '700', color: COLORS.text, marginBottom: 4 },
  hotspotScore: { fontSize: 20, fontWeight: '800' },
  hotspotTrend: { fontSize: 9, color: COLORS.muted, marginTop: 2, textTransform: 'uppercase' },
});

// Google Maps dark style
const DARK_MAP_STYLE = [
  { elementType: 'geometry', stylers: [{ color: '#0d1117' }] },
  { elementType: 'labels.text.fill', stylers: [{ color: '#7a8099' }] },
  { elementType: 'labels.text.stroke', stylers: [{ color: '#0a0c10' }] },
  { featureType: 'road', elementType: 'geometry', stylers: [{ color: '#1a1f2e' }] },
  { featureType: 'road.arterial', elementType: 'geometry', stylers: [{ color: '#222840' }] },
  { featureType: 'road.highway', elementType: 'geometry', stylers: [{ color: '#2a3050' }] },
  { featureType: 'water', elementType: 'geometry', stylers: [{ color: '#060c18' }] },
  { featureType: 'poi', stylers: [{ visibility: 'off' }] },
  { featureType: 'transit', stylers: [{ visibility: 'off' }] },
];
