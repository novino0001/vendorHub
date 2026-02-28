import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, RefreshControl } from 'react-native';
import { useAuthStore } from '../store/authStore';
import { Ionicons } from '@expo/vector-icons';
import api from '../utils/api';

export default function HomeScreen() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState({ followingCount: 0 });
  const [refreshing, setRefreshing] = useState(false);

  const loadStats = async () => {
    try {
      const followingResponse = await api.get('/vendors/me/following');
      setStats({ followingCount: followingResponse.data.total });
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadStats();
    setRefreshing(false);
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Welcome back,</Text>
          <Text style={styles.userName}>{user?.vendor_name}</Text>
        </View>
        <View style={styles.logoContainer}>
          <Ionicons name="construct" size={32} color="#2563eb" />
        </View>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <View style={styles.statIconContainer}>
            <Ionicons name="business" size={24} color="#2563eb" />
          </View>
          <Text style={styles.statValue}>{stats.followingCount}</Text>
          <Text style={styles.statLabel}>Following Firms</Text>
        </View>

        <View style={styles.statCard}>
          <View style={styles.statIconContainer}>
            <Ionicons name="people" size={24} color="#10b981" />
          </View>
          <Text style={styles.statValue}>{user?.employee_count || 0}</Text>
          <Text style={styles.statLabel}>Team Members</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Your Profile Summary</Text>
        <View style={styles.profileCard}>
          <View style={styles.profileRow}>
            <Ionicons name="briefcase-outline" size={20} color="#64748b" />
            <Text style={styles.profileText}>
              {user?.categories?.map(c => c.charAt(0).toUpperCase() + c.slice(1)).join(', ')}
            </Text>
          </View>
          <View style={styles.profileRow}>
            <Ionicons name="location-outline" size={20} color="#64748b" />
            <Text style={styles.profileText}>
              {user?.service_locations?.[0] || 'No location set'}
            </Text>
          </View>
          <View style={styles.profileRow}>
            <Ionicons name="cash-outline" size={20} color="#64748b" />
            <Text style={styles.profileText}>
              Revenue: ₹{user?.revenue?.toLocaleString('en-IN') || 0}
            </Text>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionsGrid}>
          <TouchableOpacity style={styles.actionCard}>
            <Ionicons name="search" size={24} color="#2563eb" />
            <Text style={styles.actionText}>Browse Vendors</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionCard}>
            <Ionicons name="business" size={24} color="#2563eb" />
            <Text style={styles.actionText}>View Firms</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.aboutSection}>
        <Text style={styles.aboutTitle}>About You</Text>
        <Text style={styles.aboutText}>{user?.short_bio}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 24,
    paddingTop: 60,
    backgroundColor: '#ffffff',
  },
  greeting: {
    fontSize: 16,
    color: '#64748b',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1e293b',
    marginTop: 4,
  },
  logoContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#eff6ff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 16,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 16,
    alignItems: 'center',
  },
  statIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#eff6ff',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  statValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  statLabel: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 4,
  },
  section: {
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 12,
  },
  profileCard: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 16,
    gap: 16,
  },
  profileRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  profileText: {
    flex: 1,
    fontSize: 16,
    color: '#1e293b',
  },
  actionsGrid: {
    flexDirection: 'row',
    gap: 16,
  },
  actionCard: {
    flex: 1,
    backgroundColor: '#ffffff',
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
    gap: 8,
  },
  actionText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
    textAlign: 'center',
  },
  aboutSection: {
    padding: 16,
    paddingBottom: 32,
  },
  aboutTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 12,
  },
  aboutText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#64748b',
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 16,
  },
});
