import { useState } from 'react';
import { StyleSheet, View, TextInput, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { loginUser, registerUser } from '@/services/api';
import { ThemedText } from '@/components/themed-text';

export default function LoginScreen() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [mobile, setMobile] = useState('');
  
  // Signup State
  const [name, setName] = useState('');
  const [age, setAge] = useState('25');
  const [sex, setSex] = useState('Male');
  const [height, setHeight] = useState('170');
  const [weight, setWeight] = useState('70');
  const [targetWeight, setTargetWeight] = useState('65');
  const [activityLevel, setActivityLevel] = useState('Lightly active');
  const [dietPref, setDietPref] = useState('Mixed');
  const [budget, setBudget] = useState('200');
  const [workoutType, setWorkoutType] = useState('None');

  const handleLogin = async () => {
    if (!mobile) return Alert.alert('Error', 'Please enter your mobile number');
    setIsLoading(true);
    try {
      const data = await loginUser(mobile);
      if (data.profile) {
        await AsyncStorage.setItem('user_profile', JSON.stringify(data.profile));
        router.replace('/dashboard');
      }
    } catch (error) {
      Alert.alert('Connection Failed', 'Could not reach the server or profile not found.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignup = async () => {
    if (!mobile || !name) return Alert.alert('Error', 'Please fill in all required fields');
    setIsLoading(true);
    try {
      const profileData = {
        name,
        mobile,
        age: parseInt(age),
        sex,
        height: parseFloat(height),
        weight: parseFloat(weight),
        target_weight: parseFloat(targetWeight),
        activity_level: activityLevel,
        diet_pref: dietPref,
        budget: parseFloat(budget),
        workout_type: workoutType
      };
      const data = await registerUser(profileData);
      if (data.profile) {
        await AsyncStorage.setItem('user_profile', JSON.stringify(data.profile));
        router.replace('/dashboard');
      }
    } catch (error) {
      Alert.alert('Connection Failed', 'Could not reach the server to create profile.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <ThemedText style={styles.title}>SnapDiet</ThemedText>
      
      <View style={styles.tabContainer}>
        <TouchableOpacity style={[styles.tab, isLogin && styles.activeTab]} onPress={() => setIsLogin(true)}>
          <ThemedText style={[styles.tabText, isLogin && styles.activeTabText]}>Log In</ThemedText>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.tab, !isLogin && styles.activeTab]} onPress={() => setIsLogin(false)}>
          <ThemedText style={[styles.tabText, !isLogin && styles.activeTabText]}>Sign Up</ThemedText>
        </TouchableOpacity>
      </View>

      <View style={styles.formContainer}>
        {isLogin ? (
          <>
            <ThemedText style={styles.heading}>Welcome Back</ThemedText>
            <TextInput
              style={styles.input}
              placeholder="Mobile Number"
              placeholderTextColor="#94a3b8"
              value={mobile}
              onChangeText={setMobile}
              keyboardType="phone-pad"
            />
            <TouchableOpacity style={[styles.button, isLoading && {opacity: 0.7}]} onPress={handleLogin} disabled={isLoading}>
              <ThemedText style={styles.buttonText}>{isLoading ? 'Connecting...' : 'Log In'}</ThemedText>
            </TouchableOpacity>
          </>
        ) : (
          <>
            <ThemedText style={styles.heading}>Create Profile</ThemedText>
            <TextInput style={styles.input} placeholder="Name" placeholderTextColor="#94a3b8" value={name} onChangeText={setName} />
            <TextInput style={styles.input} placeholder="Mobile Number" placeholderTextColor="#94a3b8" value={mobile} onChangeText={setMobile} keyboardType="phone-pad" />
            <TextInput style={styles.input} placeholder="Age" placeholderTextColor="#94a3b8" value={age} onChangeText={setAge} keyboardType="numeric" />
            
            <View style={styles.row}>
              <TextInput style={[styles.input, {flex: 1, marginRight: 5}]} placeholder="Height (cm)" placeholderTextColor="#94a3b8" value={height} onChangeText={setHeight} keyboardType="numeric" />
              <TextInput style={[styles.input, {flex: 1, marginLeft: 5}]} placeholder="Weight (kg)" placeholderTextColor="#94a3b8" value={weight} onChangeText={setWeight} keyboardType="numeric" />
            </View>
            <TextInput style={styles.input} placeholder="Target Weight (kg)" placeholderTextColor="#94a3b8" value={targetWeight} onChangeText={setTargetWeight} keyboardType="numeric" />
            
            <TouchableOpacity style={[styles.button, isLoading && {opacity: 0.7}]} onPress={handleSignup} disabled={isLoading}>
              <ThemedText style={styles.buttonText}>{isLoading ? 'Connecting...' : 'Complete Profile'}</ThemedText>
            </TouchableOpacity>
          </>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  contentContainer: {
    padding: 24,
    paddingTop: 80,
    alignItems: 'center',
  },
  title: {
    fontSize: 40,
    fontWeight: '800',
    color: '#34d399',
    marginBottom: 40,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#1e293b',
    borderRadius: 12,
    marginBottom: 30,
    width: '100%',
    padding: 4,
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRadius: 8,
  },
  activeTab: {
    backgroundColor: '#34d399',
  },
  tabText: {
    color: '#94a3b8',
    fontWeight: '600',
  },
  activeTabText: {
    color: '#0f172a',
    fontWeight: 'bold',
  },
  formContainer: {
    width: '100%',
    backgroundColor: '#1e293b',
    padding: 24,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
  },
  heading: {
    fontSize: 24,
    color: '#f8fafc',
    marginBottom: 20,
    fontWeight: 'bold',
  },
  input: {
    backgroundColor: '#0f172a',
    color: '#f8fafc',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#334155',
  },
  row: {
    flexDirection: 'row',
    width: '100%',
  },
  button: {
    backgroundColor: '#34d399',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: {
    color: '#0f172a',
    fontWeight: 'bold',
    fontSize: 16,
  },
});
