import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Image,
  Alert,
  Modal,
  KeyboardAvoidingView,
  Platform,
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

export default function ProfileScreen() {
  const router = useRouter();
  const { user, logout, updateProfile } = useAuthStore();
  const [editMode, setEditMode] = useState(false);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    vendor_name: user?.vendor_name || '',
    phone: user?.phone || '',
    gst_no: user?.gst_no || '',
    revenue: user?.revenue?.toString() || '',
    employee_count: user?.employee_count?.toString() || '',
    short_bio: user?.short_bio || '',
    avatar_base64: user?.avatar_base64 || '',
  });

  const [selectedCategories, setSelectedCategories] = useState<string[]>(user?.categories || []);
  const [selectedLocations, setSelectedLocations] = useState<string[]>(user?.service_locations || []);

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

  const handleSave = async () => {
    try {
      setLoading(true);
      const updateData: any = {};
      
      if (formData.vendor_name !== user?.vendor_name) updateData.vendor_name = formData.vendor_name;
      if (formData.phone !== user?.phone) updateData.phone = formData.phone;
      if (formData.gst_no !== user?.gst_no) updateData.gst_no = formData.gst_no.toUpperCase();
      if (formData.revenue !== user?.revenue?.toString()) updateData.revenue = parseFloat(formData.revenue);
      if (formData.employee_count !== user?.employee_count?.toString()) 
        updateData.employee_count = parseInt(formData.employee_count);
      if (formData.short_bio !== user?.short_bio) updateData.short_bio = formData.short_bio;
      if (formData.avatar_base64 !== user?.avatar_base64) updateData.avatar_base64 = formData.avatar_base64;
      
      if (JSON.stringify(selectedCategories) !== JSON.stringify(user?.categories)) 
        updateData.categories = selectedCategories;
      if (JSON.stringify(selectedLocations) !== JSON.stringify(user?.service_locations)) 
        updateData.service_locations = selectedLocations;

      if (Object.keys(updateData).length > 0) {
        await updateProfile(updateData);
        Alert.alert('Success', 'Profile updated successfully');
      }
      
      setEditMode(false);
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      vendor_name: user?.vendor_name || '',
      phone: user?.phone || '',
      gst_no: user?.gst_no || '',
      revenue: user?.revenue?.toString() || '',
      employee_count: user?.employee_count?.toString() || '',
      short_bio: user?.short_bio || '',
      avatar_base64: user?.avatar_base64 || '',
    });
    setSelectedCategories(user?.categories || []);
    setSelectedLocations(user?.service_locations || []);
    setEditMode(false);
  };

  const handleLogout = async () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Logout',
        style: 'destructive',
        onPress: async () => {
          await logout();
          router.replace('/');
        },
      },
    ]);
  };

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Profile</Text>
          <View style={styles.headerActions}>
            {!editMode ? (
              <TouchableOpacity style={styles.editButton} onPress={() => setEditMode(true)}>
                <Ionicons name="create-outline" size={20} color="#2563eb" />
                <Text style={styles.editButtonText}>Edit</Text>
              </TouchableOpacity>
            ) : (
              <View style={styles.editActions}>
                <TouchableOpacity style={styles.cancelButton} onPress={handleCancel}>
                  <Text style={styles.cancelButtonText}>Cancel</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.saveButton, loading && styles.saveButtonDisabled]}
                  onPress={handleSave}
                  disabled={loading}
                >
                  <Text style={styles.saveButtonText}>{loading ? 'Saving...' : 'Save'}</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>

        <View style={styles.avatarSection}>
          <TouchableOpacity
            style={styles.avatarContainer}
            onPress={editMode ? pickImage : undefined}
            disabled={!editMode}
          >
            {formData.avatar_base64 ? (
              <Image source={{ uri: formData.avatar_base64 }} style={styles.avatar} />
            ) : (
              <View style={styles.avatarPlaceholder}>
                <Ionicons name="person" size={48} color="#94a3b8" />
              </View>
            )}
            {editMode && (
              <View style={styles.cameraIconContainer}>
                <Ionicons name="camera" size={20} color="#ffffff" />
              </View>
            )}
          </TouchableOpacity>
          <Text style={styles.userName}>{formData.vendor_name}</Text>
          <Text style={styles.userEmail}>{user?.email}</Text>
        </View>

        <View style={styles.content}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Company Information</Text>
            
            <View style={styles.field}>
              <Text style={styles.label}>Company Name</Text>
              {editMode ? (
                <TextInput
                  style={styles.input}
                  value={formData.vendor_name}
                  onChangeText={(text) => setFormData({ ...formData, vendor_name: text })}
                />
              ) : (
                <Text style={styles.value}>{formData.vendor_name}</Text>
              )}
            </View>

            <View style={styles.field}>
              <Text style={styles.label}>Phone</Text>
              {editMode ? (
                <TextInput
                  style={styles.input}
                  value={formData.phone}
                  onChangeText={(text) => setFormData({ ...formData, phone: text })}
                  keyboardType="phone-pad"
                />
              ) : (
                <Text style={styles.value}>{formData.phone}</Text>
              )}
            </View>

            <View style={styles.field}>
              <Text style={styles.label}>GST Number</Text>
              {editMode ? (
                <TextInput
                  style={styles.input}
                  value={formData.gst_no}
                  onChangeText={(text) => setFormData({ ...formData, gst_no: text })}
                  autoCapitalize="characters"
                />
              ) : (
                <Text style={styles.value}>{formData.gst_no}</Text>
              )}
            </View>

            <View style={styles.row}>
              <View style={[styles.field, styles.halfWidth]}>
                <Text style={styles.label}>Revenue (₹)</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={formData.revenue}
                    onChangeText={(text) => setFormData({ ...formData, revenue: text })}
                    keyboardType="numeric"
                  />
                ) : (
                  <Text style={styles.value}>₹{parseInt(formData.revenue).toLocaleString('en-IN')}</Text>
                )}
              </View>

              <View style={[styles.field, styles.halfWidth]}>
                <Text style={styles.label}>Employees</Text>
                {editMode ? (
                  <TextInput
                    style={styles.input}
                    value={formData.employee_count}
                    onChangeText={(text) => setFormData({ ...formData, employee_count: text })}
                    keyboardType="numeric"
                  />
                ) : (
                  <Text style={styles.value}>{formData.employee_count}</Text>
                )}
              </View>
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Categories</Text>
            <View style={styles.chipsContainer}>
              {editMode ? (
                CATEGORIES.map((category) => (
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
                ))
              ) : (
                selectedCategories.map((category) => (
                  <View key={category} style={[styles.chip, styles.chipSelected]}>
                    <Text style={[styles.chipText, styles.chipTextSelected]}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </Text>
                  </View>
                ))
              )}
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Service Locations</Text>
            <View style={styles.chipsContainer}>
              {editMode ? (
                LOCATIONS.map((location) => (
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
                ))
              ) : (
                selectedLocations.map((location) => (
                  <View key={location} style={[styles.chip, styles.chipSelected]}>
                    <Text style={[styles.chipText, styles.chipTextSelected]}>{location}</Text>
                  </View>
                ))
              )}
            </View>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>About</Text>
            {editMode ? (
              <TextInput
                style={[styles.input, styles.textArea]}
                value={formData.short_bio}
                onChangeText={(text) => setFormData({ ...formData, short_bio: text })}
                multiline
                numberOfLines={4}
              />
            ) : (
              <Text style={styles.bioText}>{formData.short_bio}</Text>
            )}
          </View>

          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Ionicons name="log-out-outline" size={20} color="#ef4444" />
            <Text style={styles.logoutButtonText}>Logout</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 24,
    paddingTop: 60,
    backgroundColor: '#ffffff',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  headerActions: {
    flexDirection: 'row',
    gap: 8,
  },
  editButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#eff6ff',
  },
  editButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#2563eb',
  },
  editActions: {
    flexDirection: 'row',
    gap: 8,
  },
  cancelButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f1f5f9',
  },
  cancelButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748b',
  },
  saveButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#2563eb',
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#ffffff',
  },
  avatarSection: {
    alignItems: 'center',
    padding: 24,
    backgroundColor: '#ffffff',
  },
  avatarContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    overflow: 'hidden',
    position: 'relative',
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
  cameraIconContainer: {
    position: 'absolute',
    bottom: 0,
    right: 0,
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#2563eb',
    justifyContent: 'center',
    alignItems: 'center',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1e293b',
    marginTop: 16,
  },
  userEmail: {
    fontSize: 16,
    color: '#64748b',
    marginTop: 4,
  },
  content: {
    padding: 16,
    paddingBottom: 100,
  },
  section: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 16,
  },
  field: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#64748b',
    marginBottom: 8,
  },
  value: {
    fontSize: 16,
    color: '#1e293b',
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
  bioText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#64748b',
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: '#ffffff',
    paddingVertical: 16,
    borderRadius: 12,
    marginTop: 8,
    borderWidth: 1,
    borderColor: '#fee2e2',
  },
  logoutButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ef4444',
  },
});
