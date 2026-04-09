import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, RADIUS } from '../utils/theme';

const VARIANTS = {
  green:  { bg: 'rgba(0,229,160,0.12)',  text: COLORS.accent },
  red:    { bg: 'rgba(255,71,87,0.12)',   text: COLORS.danger },
  amber:  { bg: 'rgba(255,184,54,0.12)', text: COLORS.warn },
  blue:   { bg: 'rgba(77,159,255,0.12)', text: COLORS.accent3 },
  orange: { bg: 'rgba(255,107,53,0.12)', text: COLORS.accent2 },
};

export default function Badge({ label, variant = 'green', dot = false, style }) {
  const v = VARIANTS[variant] || VARIANTS.green;
  return (
    <View style={[styles.badge, { backgroundColor: v.bg }, style]}>
      {dot && <View style={[styles.dot, { backgroundColor: v.text }]} />}
      <Text style={[styles.label, { color: v.text }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: RADIUS.pill,
    gap: 4,
  },
  dot: {
    width: 5,
    height: 5,
    borderRadius: 999,
  },
  label: {
    fontSize: 10,
    fontWeight: '700',
    letterSpacing: 0.6,
  },
});
