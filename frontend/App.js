import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { StatusBar } from 'expo-status-bar';
import { Text, View } from 'react-native';

import HomeScreen from './src/screens/HomeScreen';
import MapScreen from './src/screens/MapScreen';
import AgentLogScreen from './src/screens/AgentLogScreen';
import OutputScreen from './src/screens/OutputScreen';
import ExplainScreen from './src/screens/ExplainScreen';

import { COLORS } from './src/utils/theme';
import { AnalysisProvider } from './src/utils/AnalysisContext';

const Tab = createBottomTabNavigator();

function TabIcon({ name, focused }) {
  const icons = {
    Home: '⌂',
    Map: '◉',
    Agents: '⚡',
    Output: '◈',
    Explain: '✦',
  };
  return (
    <Text style={{ fontSize: 16, color: focused ? COLORS.accent : COLORS.muted }}>
      {icons[name]}
    </Text>
  );
}

export default function App() {
  return (
    <AnalysisProvider>
      <NavigationContainer>
        <StatusBar style="light" />
        <Tab.Navigator
          screenOptions={({ route }) => ({
            headerShown: false,
            tabBarStyle: {
              backgroundColor: COLORS.bg2,
              borderTopColor: COLORS.border,
              borderTopWidth: 0.5,
              height: 60,
              paddingBottom: 8,
            },
            tabBarActiveTintColor: COLORS.accent,
            tabBarInactiveTintColor: COLORS.muted,
            tabBarLabelStyle: {
              fontSize: 10,
              fontWeight: '700',
              letterSpacing: 0.5,
            },
            tabBarIcon: ({ focused }) => (
              <TabIcon name={route.name} focused={focused} />
            ),
          })}
        >
          <Tab.Screen name="Home" component={HomeScreen} />
          <Tab.Screen name="Map" component={MapScreen} />
          <Tab.Screen name="Agents" component={AgentLogScreen} />
          <Tab.Screen name="Output" component={OutputScreen} />
          <Tab.Screen name="Explain" component={ExplainScreen} />
        </Tab.Navigator>
      </NavigationContainer>
    </AnalysisProvider>
  );
}
