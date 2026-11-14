import { useEffect, useState } from 'react';
import { StyleSheet, View, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { getDailyLog } from '@/services/api';
import { ThemedText } from '@/components/themed-text';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function DashboardScreen() {
  const router = useRouter();
  const [profile, setProfile] = useState<any>(null);
  const [dailyLog, setDailyLog] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const profileStr = await AsyncStorage.getItem('user_profile');
        if (!profileStr) {
          router.replace('/login');
          return;
        }
        setProfile(JSON.parse(profileStr));
        
        const logData = await getDailyLog();
        setDailyLog(logData);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const handleLogout = async () => {
    await AsyncStorage.removeItem('user_profile');
    router.replace('/login');
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#34d399" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <ThemedText style={styles.greeting}>Hello, {profile?.name}</ThemedText>
          <TouchableOpacity onPress={handleLogout} style={styles.logoutBtn}>
            <ThemedText style={styles.logoutText}>Logout</ThemedText>
          </TouchableOpacity>
        </View>

        <View style={styles.card}>
          <ThemedText style={styles.cardTitle}>Daily Calories</ThemedText>
          <View style={styles.calorieRow}>
            <View style={styles.statBox}>
              <ThemedText style={styles.statValue}>{dailyLog?.calories || 0}</ThemedText>
              <ThemedText style={styles.statLabel}>Consumed</ThemedText>
            </View>
            <View style={styles.statBox}>
              <ThemedText style={styles.statValue}>{Math.round(profile?.target_calories || 2000)}</ThemedText>
              <ThemedText style={styles.statLabel}>Target</ThemedText>
            </View>
          </View>
        </View>

        <View style={styles.card}>
          <ThemedText style={styles.cardTitle}>Macros</ThemedText>
          <View style={styles.macroRow}>
            <View style={styles.macroBox}>
              <ThemedText style={styles.macroValue}>{dailyLog?.protein || 0}g</ThemedText>
              <ThemedText style={styles.macroLabel}>Protein</ThemedText>
            </View>
            <View style={styles.macroBox}>
              <ThemedText style={styles.macroValue}>{dailyLog?.carbs || 0}g</ThemedText>
              <ThemedText style={styles.macroLabel}>Carbs</ThemedText>
            </View>
            <View style={styles.macroBox}>
              <ThemedText style={styles.macroValue}>{dailyLog?.fats || 0}g</ThemedText>
              <ThemedText style={styles.macroLabel}>Fats</ThemedText>
            </View>
          </View>
        </View>
        
        <View style={styles.card}>
          <ThemedText style={styles.cardTitle}>Diet Plan Preference</ThemedText>
          <ThemedText style={styles.infoText}>You are on a {profile?.diet_pref} diet with a {profile?.workout_type} workout routine.</ThemedText>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: '#0f172a',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#f8fafc',
  },
  logoutBtn: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#1e293b',
    borderRadius: 8,
  },
  logoutText: {
    color: '#ef4444',
    fontWeight: 'bold',
  },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
  },
  cardTitle: {
    fontSize: 18,
    color: '#94a3b8',
    marginBottom: 16,
    fontWeight: '600',
  },
  calorieRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statBox: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#34d399',
  },
  statLabel: {
    color: '#64748b',
    marginTop: 4,
  },
  macroRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  macroBox: {
    alignItems: 'center',
    flex: 1,
  },
  macroValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#38bdf8',
  },
  macroLabel: {
    color: '#64748b',
    marginTop: 4,
  },
  infoText: {
    color: '#f8fafc',
    fontSize: 16,
    lineHeight: 24,
  }
});
