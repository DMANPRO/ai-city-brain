import React, { useState, useEffect } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, ScrollView,
  StyleSheet, ActivityIndicator, Alert, FlatList,
} from 'react-native';
import * as Location from 'expo-location';
import { useNavigation } from '@react-navigation/native';

import { COLORS, SPACING, RADIUS, scoreColor, scoreLabel } from '../utils/theme';
import { useAnalysis } from '../utils/AnalysisContext';
import { analyze, searchLocations, fetchWeather } from '../utils/api';
import Badge from '../components/Badge';
import Card from '../components/Card';

const WEATHER_OPTIONS = [
  { label: '☀ Clear',  value: 'clear' },
  { label: '🌧 Rain',  value: 'rain' },
  { label: '🌫 Fog',   value: 'fog' },
  { label: '⛈ Storm', value: 'storm' },
  { label: '☁ Cloudy', value: 'cloudy' },
];

const TIME_OPTIONS = [
  { label: '🟢 Live Now',         value: null },
  { label: '07:00 — Morning Rush', value: 7 },
  { label: '09:00 — Peak Hour',    value: 9 },
  { label: '12:00 — Afternoon',    value: 12 },
  { label: '17:00 — Evening Peak', value: 17 },
  { label: '20:00 — Night',        value: 20 },
  { label: '23:00 — Late Night',   value: 23 },
];

const SIM_OPTIONS = ['T+0 (Now)', 'T+5 min', 'T+10 min', 'T+15 min'];

export default function HomeScreen() {
  const navigation = useNavigation();
  const { result, setResult, loading, setLoading, params, setParams } = useAnalysis();

  const [locQuery, setLocQuery] = useState(params.location);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [timeIdx, setTimeIdx] = useState(0);
  const [simIdx, setSimIdx] = useState(0);

  // Auto-fetch weather from GPS on mount
  useEffect(() => {
    (async () => {
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status !== 'granted') return;
        const loc = await Location.getCurrentPositionAsync({});
        const weather = await fetchWeather(loc.coords.latitude, loc.coords.longitude);
        setParams(p => ({ ...p, weather: weather.condition }));
      } catch (_) {
        // silently fail — user can pick weather manually
      }
    })();
  }, []);

  async function handleLocInput(text) {
    setLocQuery(text);
    if (text.length < 2) { setSuggestions([]); setShowSuggestions(false); return; }
    try {
      const res = await searchLocations(text);
      setSuggestions(res);
      setShowSuggestions(true);
    } catch (_) {
      // offline fallback list
      const fallback = ['Koramangala','Marathahalli','Indiranagar','Whitefield','HSR Layout','BTM Layout','Silk Board','Electronic City','Hebbal','MG Road'];
      setSuggestions(fallback.filter(l => l.toLowerCase().includes(text.toLowerCase())).map(l => ({ name: l })));
      setShowSuggestions(true);
    }
  }

  function selectSuggestion(item) {
    const name = typeof item === 'string' ? item : item.name;
    setLocQuery(name);
    setParams(p => ({ ...p, location: name }));
    setShowSuggestions(false);
    setSuggestions([]);
  }

  async function handleAnalyze() {
    setLoading(true);
    const time = TIME_OPTIONS[timeIdx].value;
    const simulation = simIdx * 5;
    setParams(p => ({ ...p, location: locQuery, time, simulation }));
    try {
      const data = await analyze({ location: locQuery, time, weather: params.weather, simulation });
      setResult(data);
      navigation.navigate('Agents');
    } catch (err) {
      Alert.alert('API Error', err.message || 'Could not reach backend. Check BASE_URL in api.js.');
    } finally {
      setLoading(false);
    }
  }

  const latestScore = result?.congestion_score;
  const latestSpeed = result?.avg_speed;
  const latestIncidents = result?.incident_count;

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>Traffic{'\n'}<Text style={{ color: COLORS.accent }}>Intelligence</Text></Text>
          <Text style={styles.subtitle}>Bengaluru city-level ops</Text>
        </View>
        <View style={styles.livePill}>
          <View style={styles.liveDot} />
          <Text style={styles.liveText}>LIVE</Text>
        </View>
      </View>

      {/* Location input */}
      <View>
        <Text style={styles.inputLabel}>Location</Text>
        <View style={styles.inputWrap}>
          <TextInput
            style={styles.textInput}
            value={locQuery}
            onChangeText={handleLocInput}
            placeholder="Search area in Bengaluru..."
            placeholderTextColor={COLORS.muted}
            autoCorrect={false}
          />
          <Text style={styles.inputIcon}>⌕</Text>
        </View>
        {showSuggestions && suggestions.length > 0 && (
          <View style={styles.suggestionBox}>
            {suggestions.slice(0, 5).map((item, i) => (
              <TouchableOpacity key={i} style={[styles.suggestionItem, i < suggestions.length - 1 && styles.suggestionBorder]} onPress={() => selectSuggestion(item)}>
                <Text style={styles.suggestionIcon}>📍</Text>
                <Text style={styles.suggestionText}>{typeof item === 'string' ? item : item.name}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
      </View>

      {/* Weather chips */}
      <View>
        <Text style={styles.inputLabel}>Weather Condition</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginHorizontal: -SPACING.xl }}>
          <View style={{ flexDirection: 'row', gap: SPACING.sm, paddingHorizontal: SPACING.xl }}>
            {WEATHER_OPTIONS.map(w => (
              <TouchableOpacity
                key={w.value}
                style={[styles.chip, params.weather === w.value && styles.chipSel]}
                onPress={() => setParams(p => ({ ...p, weather: w.value }))}
              >
                <Text style={[styles.chipText, params.weather === w.value && styles.chipTextSel]}>{w.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </ScrollView>
      </View>

      {/* Time + Simulation pickers */}
      <View style={styles.row}>
        <View style={{ flex: 1 }}>
          <Text style={styles.inputLabel}>Time of Analysis</Text>
          <ScrollView style={styles.pickerBox} showsVerticalScrollIndicator={false}>
            {TIME_OPTIONS.map((t, i) => (
              <TouchableOpacity key={i} onPress={() => setTimeIdx(i)} style={[styles.pickerItem, i === timeIdx && styles.pickerItemSel]}>
                <Text style={[styles.pickerText, i === timeIdx && styles.pickerTextSel]}>{t.label}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
        <View style={{ flex: 1 }}>
          <Text style={styles.inputLabel}>Simulation</Text>
          <View style={styles.pickerBox}>
            {SIM_OPTIONS.map((s, i) => (
              <TouchableOpacity key={i} onPress={() => setSimIdx(i)} style={[styles.pickerItem, i === simIdx && styles.pickerItemSel]}>
                <Text style={[styles.pickerText, i === simIdx && styles.pickerTextSel]}>{s}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>

      {/* Stat cards */}
      <View style={styles.statsRow}>
        <Card style={styles.statCard}>
          <Text style={[styles.statVal, { color: latestScore ? scoreColor(latestScore) : COLORS.accent }]}>
            {latestScore ? latestScore.toFixed(1) : '—'}
          </Text>
          <Text style={styles.statLbl}>Congestion Score</Text>
        </Card>
        <Card style={styles.statCard}>
          <Text style={[styles.statVal, { color: COLORS.warn }]}>
            {latestSpeed ? `${latestSpeed}` : '—'}
            {latestSpeed ? <Text style={{ fontSize: 12 }}> km/h</Text> : null}
          </Text>
          <Text style={styles.statLbl}>Avg Speed</Text>
        </Card>
        <Card style={styles.statCard}>
          <Text style={[styles.statVal, { color: COLORS.danger }]}>
            {latestIncidents ?? '—'}
          </Text>
          <Text style={styles.statLbl}>Incidents</Text>
        </Card>
      </View>

      {/* Analyze button */}
      <TouchableOpacity style={styles.analyzeBtn} onPress={handleAnalyze} disabled={loading}>
        {loading
          ? <ActivityIndicator color="#060a08" />
          : <Text style={styles.analyzeBtnText}>⚡ Run City Brain Analysis</Text>}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: COLORS.bg },
  content: { padding: SPACING.xl, gap: SPACING.lg, paddingBottom: 40 },

  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  title: { fontSize: 26, fontWeight: '800', color: COLORS.text, lineHeight: 30 },
  subtitle: { fontSize: 12, color: COLORS.muted, marginTop: 4 },
  livePill: { flexDirection: 'row', alignItems: 'center', gap: 6, backgroundColor: 'rgba(0,229,160,0.08)', borderWidth: 0.5, borderColor: 'rgba(0,229,160,0.2)', borderRadius: RADIUS.pill, paddingHorizontal: 10, paddingVertical: 5 },
  liveDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: COLORS.accent },
  liveText: { fontSize: 10, fontWeight: '700', color: COLORS.accent, letterSpacing: 0.6 },

  inputLabel: { fontSize: 10, fontWeight: '700', color: COLORS.muted, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6 },
  inputWrap: { position: 'relative' },
  textInput: { backgroundColor: COLORS.bg3, borderWidth: 0.5, borderColor: COLORS.border2, borderRadius: RADIUS.md, color: COLORS.text, fontSize: 13, padding: SPACING.md, paddingRight: 40 },
  inputIcon: { position: 'absolute', right: 12, top: 12, fontSize: 14, color: COLORS.muted },
  suggestionBox: { backgroundColor: COLORS.bg3, borderWidth: 0.5, borderColor: COLORS.border2, borderRadius: RADIUS.md, marginTop: 4, overflow: 'hidden' },
  suggestionItem: { flexDirection: 'row', alignItems: 'center', gap: 8, padding: SPACING.md },
  suggestionBorder: { borderBottomWidth: 0.5, borderBottomColor: COLORS.border },
  suggestionIcon: { fontSize: 11 },
  suggestionText: { fontSize: 12, color: COLORS.muted },

  chip: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: RADIUS.pill, borderWidth: 0.5, borderColor: COLORS.border2, backgroundColor: COLORS.bg3 },
  chipSel: { backgroundColor: 'rgba(0,229,160,0.12)', borderColor: 'rgba(0,229,160,0.3)' },
  chipText: { fontSize: 12, fontWeight: '600', color: COLORS.muted },
  chipTextSel: { color: COLORS.accent },

  row: { flexDirection: 'row', gap: SPACING.md },
  pickerBox: { backgroundColor: COLORS.bg3, borderWidth: 0.5, borderColor: COLORS.border2, borderRadius: RADIUS.md, maxHeight: 140, overflow: 'hidden' },
  pickerItem: { paddingHorizontal: 12, paddingVertical: 8 },
  pickerItemSel: { backgroundColor: 'rgba(0,229,160,0.08)' },
  pickerText: { fontSize: 11, color: COLORS.muted },
  pickerTextSel: { color: COLORS.accent, fontWeight: '700' },

  statsRow: { flexDirection: 'row', gap: SPACING.sm },
  statCard: { flex: 1, alignItems: 'flex-start', gap: 4 },
  statVal: { fontSize: 22, fontWeight: '800' },
  statLbl: { fontSize: 9, color: COLORS.muted, textTransform: 'uppercase', letterSpacing: 0.8 },

  analyzeBtn: { backgroundColor: COLORS.accent, borderRadius: RADIUS.lg, paddingVertical: 15, alignItems: 'center', justifyContent: 'center' },
  analyzeBtnText: { fontSize: 14, fontWeight: '800', color: '#060a08', letterSpacing: 0.2 },
});
