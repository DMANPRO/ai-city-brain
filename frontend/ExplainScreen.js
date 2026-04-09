import React, { useState, useRef } from 'react';
import {
  View, Text, TextInput, TouchableOpacity, ScrollView,
  StyleSheet, KeyboardAvoidingView, Platform,
} from 'react-native';
import * as Notifications from 'expo-notifications';

import { COLORS, SPACING, RADIUS, scoreColor } from '../utils/theme';
import { useAnalysis } from '../utils/AnalysisContext';
import Badge from '../components/Badge';
import Card from '../components/Card';

// Configure notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

const SCENARIO_RESPONSES = [
  (loc) => `If rain stops: weather multiplier drops from 1.3x → 1.0x. Estimated score falls from ${loc} to ~71.8. Normalize time: 14 min.`,
  () => `Adding VIP convoy at 7pm: Priority Agent clears 2.1km corridor. Surrounding roads: +8 min average delay. Score impact: +6.2.`,
  () => `Closing Intermediate Ring Road: Propagation shows 34% traffic shift to ORR. Origin score → 100. Alt route Sarjapur: +11 min travel.`,
  () => `Signal timing +30s on 80ft Road: Estimated 22% queue reduction at junction. Recommend cascade to 4 downstream signals.`,
  () => `Deploying 2 traffic marshals at junction: Manual override reduces score by est. 15 points in 10 min. Recommend junction 5th Block.`,
];

const CONTROL_ACTIONS = [
  {
    icon: '⏱',
    title: 'Extend green phase — 5th Block junction',
    sub: '+45s outbound signal — reduces backlog est. 18%',
    badge: 'HIGH', variant: 'green',
  },
  {
    icon: '🔀',
    title: 'Divert via Sarjapur Road alternate',
    sub: 'Matrix routing: 14 min faster via alternate corridor',
    badge: 'MED', variant: 'amber',
  },
  {
    icon: '🚑',
    title: 'Priority corridor active — pre-cleared',
    sub: 'Ambulance ETA: 6 min on active corridor',
    badge: 'LIVE', variant: 'blue',
  },
];

export default function ExplainScreen() {
  const { result, params } = useAnalysis();
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Ask any scenario — e.g. "What if it stops raining?" or "Add a VIP convoy at 7pm"' },
  ]);
  const [scIdx, setScIdx] = useState(0);
  const scrollRef = useRef(null);

  const score = result?.congestion_score ?? 93.6;
  const location = params.location ?? 'Koramangala';

  async function requestNotifPermission() {
    const { status } = await Notifications.requestPermissionsAsync();
    if (status === 'granted') {
      await Notifications.scheduleNotificationAsync({
        content: {
          title: '⚠ City Brain Alert',
          body: `Congestion CRITICAL at ${location} — Score: ${score.toFixed(1)}`,
        },
        trigger: null,
      });
    }
  }

  function sendScenario() {
    if (!input.trim()) return;
    const userMsg = { role: 'user', text: input.trim() };
    setMessages(m => [...m, userMsg]);
    setInput('');
    setTimeout(() => {
      const aiReply = { role: 'ai', text: SCENARIO_RESPONSES[scIdx % SCENARIO_RESPONSES.length](score.toFixed(1)) };
      setMessages(m => [...m, aiReply]);
      setScIdx(i => i + 1);
      setTimeout(() => scrollRef.current?.scrollToEnd({ animated: true }), 100);
    }, 900);
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
      <ScrollView ref={scrollRef} style={styles.screen} contentContainerStyle={styles.content}>

        {/* Header */}
        <View>
          <Text style={styles.title}>Explanation Agent</Text>
          <Text style={styles.subtitle}>Plain-English city operator summary</Text>
        </View>

        {/* Push notification trigger */}
        <TouchableOpacity style={styles.notifBanner} onPress={requestNotifPermission}>
          <Text style={styles.notifIcon}>🔔</Text>
          <View style={{ flex: 1 }}>
            <Text style={styles.notifTitle}>Enable congestion alerts</Text>
            <Text style={styles.notifSub}>Get push notification when score exceeds threshold</Text>
          </View>
          <Badge label="TAP" variant="amber" />
        </TouchableOpacity>

        {/* Why card */}
        <Card>
          <Text style={styles.explainIcon}>🧠</Text>
          <Text style={styles.explainTitle}>Why is {location} congested?</Text>
          <Text style={styles.explainBody}>
            <Text style={styles.em}>Evening peak traffic</Text> (5–8pm) has compressed average speed to <Text style={styles.em}>{result?.avg_speed ?? 12} km/h</Text> — {result?.trend_delta?.toFixed(0) ?? 78}% slower than free-flow.{'\n\n'}
            Three compounding factors: an <Text style={styles.em}>accident near {location}</Text> is blocking one lane, active <Text style={styles.em}>road works</Text> have reduced capacity ~40%, and <Text style={styles.em}>{params.weather}</Text> is adding a {params.weather === 'rain' ? '1.3x' : '1.0x'} slowdown multiplier.{'\n\n'}
            The Propagation Agent predicts congestion will <Text style={styles.em}>spread to adjacent zones</Text> in 10–15 minutes if signal timing isn't adjusted.
          </Text>
        </Card>

        {/* Control actions */}
        <Card>
          <Text style={styles.explainIcon}>🚦</Text>
          <Text style={styles.explainTitle}>Recommended control actions</Text>
          <View style={{ gap: 8 }}>
            {CONTROL_ACTIONS.map((a, i) => (
              <View key={i} style={styles.actionChip}>
                <Text style={{ fontSize: 18 }}>{a.icon}</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.actionTitle}>{a.title}</Text>
                  <Text style={styles.actionSub}>{a.sub}</Text>
                </View>
                <Badge label={a.badge} variant={a.variant} />
              </View>
            ))}
          </View>
        </Card>

        {/* What-if simulator */}
        <Card>
          <Text style={styles.explainIcon}>💬</Text>
          <Text style={styles.explainTitle}>What-If Scenario Simulator</Text>
          <View style={{ gap: 8 }}>
            {messages.map((m, i) => (
              <View key={i} style={[styles.bubble, m.role === 'user' ? styles.bubbleUser : styles.bubbleAI]}>
                <Text style={[styles.bubbleText, m.role === 'user' ? styles.bubbleTextUser : styles.bubbleTextAI]}>{m.text}</Text>
              </View>
            ))}
          </View>
          <View style={styles.scenarioInputRow}>
            <TextInput
              style={styles.scenarioInput}
              value={input}
              onChangeText={setInput}
              placeholder="Type a what-if scenario..."
              placeholderTextColor={COLORS.muted}
              onSubmitEditing={sendScenario}
              returnKeyType="send"
            />
            <TouchableOpacity style={styles.sendBtn} onPress={sendScenario}>
              <Text style={{ fontSize: 16, color: '#060a08', fontWeight: '800' }}>↗</Text>
            </TouchableOpacity>
          </View>
        </Card>

      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: COLORS.bg },
  content: { padding: SPACING.lg, gap: SPACING.md, paddingBottom: 60 },

  title: { fontSize: 18, fontWeight: '800', color: COLORS.text },
  subtitle: { fontSize: 11, color: COLORS.muted, marginTop: 2 },

  notifBanner: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    backgroundColor: 'rgba(255,184,54,0.06)',
    borderWidth: 0.5, borderColor: 'rgba(255,184,54,0.2)',
    borderRadius: RADIUS.md, padding: SPACING.md,
  },
  notifIcon: { fontSize: 18 },
  notifTitle: { fontSize: 12, fontWeight: '700', color: COLORS.text },
  notifSub: { fontSize: 10, color: COLORS.muted },

  explainIcon: { fontSize: 20, marginBottom: 6 },
  explainTitle: { fontSize: 13, fontWeight: '700', color: COLORS.text, marginBottom: 8 },
  explainBody: { fontSize: 12, lineHeight: 20, color: COLORS.muted },
  em: { color: COLORS.text, fontWeight: '600' },

  actionChip: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    padding: SPACING.md, backgroundColor: COLORS.bg3,
    borderRadius: RADIUS.sm, borderWidth: 0.5, borderColor: COLORS.border,
  },
  actionTitle: { fontSize: 12, fontWeight: '700', color: COLORS.text, marginBottom: 2 },
  actionSub: { fontSize: 10, color: COLORS.muted },

  bubble: { padding: SPACING.md, borderRadius: RADIUS.md, maxWidth: '90%' },
  bubbleUser: { backgroundColor: 'rgba(0,229,160,0.08)', borderWidth: 0.5, borderColor: 'rgba(0,229,160,0.15)', alignSelf: 'flex-end' },
  bubbleAI: { backgroundColor: COLORS.bg3, borderWidth: 0.5, borderColor: COLORS.border },
  bubbleText: { fontSize: 12, lineHeight: 18 },
  bubbleTextUser: { color: COLORS.accent },
  bubbleTextAI: { color: COLORS.muted },

  scenarioInputRow: { flexDirection: 'row', gap: 8, marginTop: 10 },
  scenarioInput: {
    flex: 1, backgroundColor: COLORS.bg3, borderWidth: 0.5,
    borderColor: COLORS.border2, borderRadius: RADIUS.md,
    color: COLORS.text, fontSize: 12, padding: SPACING.md,
  },
  sendBtn: {
    width: 42, backgroundColor: COLORS.accent, borderRadius: RADIUS.md,
    alignItems: 'center', justifyContent: 'center',
  },
});
