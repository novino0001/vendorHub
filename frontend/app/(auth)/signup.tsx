import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../store/authStore';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';

const CATEGORIES = ['civil', 'mechanical', 'electrical', 'transport'];
const LOCATIONS = [
  'Maharashtra - Mumbai',
  'Karnataka - Bangalore',
  'Tamil Nadu - Chennai',
  'Delhi - New Delhi',
  'Gujarat - Ahmedabad',
  'West Bengal - Kolkata',
  'Rajasthan - Jaipur',
  'Telangana - Hyderabad',
];

export default function SignupScreen() {
  const router = useRouter();
  const { signup } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    vendor_name: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    gst_no: '',
    revenue: '',
    employee_count: '',
    short_bio: '',
    avatar_base64: '',
  });

  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedLocations, setSelectedLocations] = useState<string[]>([]);

  const toggleCategory = (category: string) => {
    setSelectedCategories((prev) =>
      prev.includes(category) ? prev.filter((c) => c !== category) : [...prev, category]
    );
  };

  const toggleLocation = (location: string) => {
    setSelectedLocations((prev) =>
      prev.includes(location) ? prev.filter((l) => l !== location) : [...prev, location]
    );
  };

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: 'images',
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.5,
      base64: true,
    });

    if (!result.canceled && result.assets[0].base64) {
      setFormData({ ...formData, avatar_base64: `data:image/jpeg;base64,${result.assets[0].base64}` });
    }
  };

  const handleSignup = async () => {
    // Validation
    if (
      !formData.vendor_name ||
      !formData.email ||
      !formData.phone ||
      !formData.password ||
      !formData.gst_no ||
      !formData.revenue ||
      !formData.employee_count ||
      !formData.short_bio
    ) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    if (selectedCategories.length === 0) {
      Alert.alert('Error', 'Please select at least one category');
      return;
    }

    if (selectedLocations.length === 0) {
      Alert.alert('Error', 'Please select at least one service location');
      return;
    }

    try {
      setLoading(true);
      const signupData = {
        vendor_name: formData.vendor_name,
        email: formData.email.toLowerCase().trim(),
        phone: formData.phone,
        password: formData.password,
        gst_no: formData.gst_no.toUpperCase(),
        revenue: parseFloat(formData.revenue),
        employee_count: parseInt(formData.employee_count),
        categories: selectedCategories,
        service_locations: selectedLocations,
        short_bio: formData.short_bio,
        avatar_base64: formData.avatar_base64 || null,
      };

      await signup(signupData);
      router.replace('/(tabs)');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail;
      if (typeof errorMessage === 'string') {
        Alert.alert('Signup Failed', errorMessage);
      } else if (Array.isArray(errorMessage)) {
        Alert.alert('Validation Error', errorMessage.map((e: any) => e.msg).join('\n'));
      } else {
        Alert.alert('Signup Failed', 'Please check your information and try again');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#1e293b" />
          </TouchableOpacity>
          <Text style={styles.title}>Create Account</Text>
          <Text style={styles.subtitle}>Join the contractor network</Text>
        </View>

        <View style={styles.form}>
          {/* Profile Picture */}
          <View style={styles.avatarSection}>
            <TouchableOpacity style={styles.avatarContainer} onPress={pickImage}>
              {formData.avatar_base64 ? (
                <Image source={{ uri: formData.avatar_base64 }} style={styles.avatar} />
              ) : (
                <View style={styles.avatarPlaceholder}>
                  <Ionicons name="camera" size={32} color="#64748b" />
                </View>
              )}
            </TouchableOpacity>
            <Text style={styles.avatarLabel}>Tap to add profile picture</Text>
          </View>

          {/* Basic Info */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Company Name *</Text>
            <TextInput
              style={styles.input}
              placeholder="Your contractor company name"
              value={formData.vendor_name}
              onChangeText={(text) => setFormData({ ...formData, vendor_name: text })}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Email *</Text>
            <TextInput
              style={styles.input}
              placeholder="your@email.com"
              value={formData.email}
              onChangeText={(text) => setFormData({ ...formData, email: text })}
              autoCapitalize="none"
              keyboardType="email-address"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Phone *</Text>
            <TextInput
              style={styles.input}
              placeholder="+919876543210"
              value={formData.phone}
              onChangeText={(text) => setFormData({ ...formData, phone: text })}
              keyboardType="phone-pad"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>GST Number *</Text>
            <TextInput
              style={styles.input}
              placeholder="29ABCDE1234F1Z5"
              value={formData.gst_no}
              onChangeText={(text) => setFormData({ ...formData, gst_no: text })}
              autoCapitalize="characters"
            />
          </View>

          <View style={styles.row}>
            <View style={[styles.inputGroup, styles.halfWidth]}>
              <Text style={styles.label}>Revenue (₹) *</Text>
              <TextInput
                style={styles.input}
                placeholder="1000000"
                value={formData.revenue}
                onChangeText={(text) => setFormData({ ...formData, revenue: text })}
                keyboardType="numeric"
              />
            </View>

            <View style={[styles.inputGroup, styles.halfWidth]}>
              <Text style={styles.label}>Employees *</Text>
              <TextInput
                style={styles.input}
                placeholder="25"
                value={formData.employee_count}
                onChangeText={(text) => setFormData({ ...formData, employee_count: text })}
                keyboardType="numeric"
              />
            </View>
          </View>

          {/* Categories */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Categories * (Select at least one)</Text>
            <View style={styles.chipsContainer}>
              {CATEGORIES.map((category) => (
                <TouchableOpacity
                  key={category}
                  style={[
                    styles.chip,
                    selectedCategories.includes(category) && styles.chipSelected,
                  ]}
                  onPress={() => toggleCategory(category)}
                >
                  <Text
                    style={[
                      styles.chipText,
                      selectedCategories.includes(category) && styles.chipTextSelected,
                    ]}
                  >
                    {category.charAt(0).toUpperCase() + category.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Service Locations */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Service Locations * (Select at least one)</Text>
            <View style={styles.chipsContainer}>
              {LOCATIONS.map((location) => (
                <TouchableOpacity
                  key={location}
                  style={[
                    styles.chip,
                    selectedLocations.includes(location) && styles.chipSelected,
                  ]}
                  onPress={() => toggleLocation(location)}
                >
                  <Text
                    style={[
                      styles.chipText,
                      selectedLocations.includes(location) && styles.chipTextSelected,
                    ]}
                  >
                    {location}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          {/* Bio */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Short Bio *</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Tell us about your company and expertise..."
              value={formData.short_bio}
              onChangeText={(text) => setFormData({ ...formData, short_bio: text })}
              multiline
              numberOfLines={4}
            />
          </View>

          {/* Password */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Password *</Text>
            <View style={styles.passwordContainer}>
              <TextInput
                style={styles.passwordInput}
                placeholder="Create a strong password"
                value={formData.password}
                onChangeText={(text) => setFormData({ ...formData, password: text })}
                secureTextEntry={!showPassword}
              />
              <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                <Ionicons
                  name={showPassword ? 'eye-off-outline' : 'eye-outline'}
                  size={20}
                  color="#64748b"
                />
              </TouchableOpacity>
            </View>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Confirm Password *</Text>
            <TextInput
              style={styles.input}
              placeholder="Re-enter your password"
              value={formData.confirmPassword}
              onChangeText={(text) => setFormData({ ...formData, confirmPassword: text })}
              secureTextEntry
            />
          </View>

          <TouchableOpacity
            style={[styles.signupButton, loading && styles.signupButtonDisabled]}
            onPress={handleSignup}
            disabled={loading}
          >
            <Text style={styles.signupButtonText}>{loading ? 'Creating Account...' : 'Sign Up'}</Text>
          </TouchableOpacity>

          <View style={styles.footer}>
            <Text style={styles.footerText}>Already have an account? </Text>
            <TouchableOpacity onPress={() => router.push('/(auth)/login')}>
              <Text style={styles.footerLink}>Log In</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: 32,
  },
  header: {
    paddingTop: 60,
    paddingHorizontal: 24,
    paddingBottom: 24,
  },
  backButton: {
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
  },
  form: {
    paddingHorizontal: 24,
  },
  avatarSection: {
    alignItems: 'center',
    marginBottom: 24,
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    overflow: 'hidden',
  },
  avatar: {
    width: '100%',
    height: '100%',
  },
  avatarPlaceholder: {
    width: '100%',
    height: '100%',
    backgroundColor: '#f1f5f9',
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarLabel: {
    marginTop: 8,
    fontSize: 14,
    color: '#64748b',
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1e293b',
    backgroundColor: '#f8fafc',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  row: {
    flexDirection: 'row',
    gap: 12,
  },
  halfWidth: {
    flex: 1,
  },
  chipsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  chip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#ffffff',
  },
  chipSelected: {
    backgroundColor: '#2563eb',
    borderColor: '#2563eb',
  },
  chipText: {
    fontSize: 14,
    color: '#64748b',
  },
  chipTextSelected: {
    color: '#ffffff',
    fontWeight: '600',
  },
  passwordContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    borderRadius: 12,
    paddingHorizontal: 16,
    backgroundColor: '#f8fafc',
  },
  passwordInput: {
    flex: 1,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1e293b',
  },
  signupButton: {
    backgroundColor: '#2563eb',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  signupButtonDisabled: {
    opacity: 0.6,
  },
  signupButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 24,
  },
  footerText: {
    fontSize: 14,
    color: '#64748b',
  },
  footerLink: {
    fontSize: 14,
    color: '#2563eb',
    fontWeight: '600',
  },
});
