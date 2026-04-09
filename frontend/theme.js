export const COLORS = {
  bg: '#0a0c10',
  bg2: '#11141b',
  bg3: '#181c26',
  border: 'rgba(255,255,255,0.08)',
  border2: 'rgba(255,255,255,0.14)',
  text: '#e8eaf0',
  muted: '#7a8099',
  accent: '#00e5a0',
  accent2: '#ff6b35',
  accent3: '#4d9fff',
  warn: '#ffb836',
  danger: '#ff4757',
};

export const FONTS = {
  mono: 'SpaceMono',    // load via expo-font or use Platform.select
  sans: 'System',
};

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 24,
};

export const RADIUS = {
  sm: 8,
  md: 10,
  lg: 12,
  xl: 16,
  pill: 999,
};

// Congestion score → color
export function scoreColor(score) {
  if (score >= 80) return COLORS.danger;
  if (score >= 60) return COLORS.accent2;
  if (score >= 40) return COLORS.warn;
  return COLORS.accent;
}

// Congestion score → label
export function scoreLabel(score) {
  if (score >= 80) return 'CRITICAL';
  if (score >= 60) return 'HIGH';
  if (score >= 40) return 'MEDIUM';
  return 'LOW';
}
