import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Image,
  RefreshControl,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import api from '../utils/api';

interface Firm {
  id: string;
  name: string;
  category: string;
  office_location: string;
  description: string;
  logo_base64?: string;
  is_following: boolean;
}

export default function FirmsScreen() {
  const [firms, setFirms] = useState<Firm[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const loadFirms = async (pageNum = 1) => {
    if (loading) return;
    
    try {
      setLoading(true);
      const response = await api.get('/firms', {
        params: { page: pageNum, per_page: 10 },
      });
      
      if (pageNum === 1) {
        setFirms(response.data.firms);
      } else {
        setFirms((prev) => [...prev, ...response.data.firms]);
      }
      
      setHasMore(response.data.firms.length === 10);
      setPage(pageNum);
    } catch (error) {
      console.error('Error loading firms:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFirms(1);
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadFirms(1);
    setRefreshing(false);
  };

  const loadMore = () => {
    if (hasMore && !loading) {
      loadFirms(page + 1);
    }
  };

  const handleFollowToggle = async (firm: Firm) => {
    try {
      if (firm.is_following) {
        await api.delete(`/firms/${firm.id}/unfollow`);
        Alert.alert('Success', `Unfollowed ${firm.name}`);
      } else {
        await api.post(`/firms/${firm.id}/follow`);
        Alert.alert('Success', `Now following ${firm.name}`);
      }
      
      // Update local state
      setFirms((prev) =>
        prev.map((f) =>
          f.id === firm.id ? { ...f, is_following: !f.is_following } : f
        )
      );
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to update follow status');
    }
  };

  const renderFirm = ({ item }: { item: Firm }) => (
    <View style={styles.firmCard}>
      <View style={styles.firmHeader}>
        {item.logo_base64 ? (
          <Image source={{ uri: item.logo_base64 }} style={styles.logo} />
        ) : (
          <View style={styles.logoPlaceholder}>
            <Ionicons name="business" size={32} color="#94a3b8" />
          </View>
        )}
        <View style={styles.firmInfo}>
          <Text style={styles.firmName}>{item.name}</Text>
          <View style={styles.categoryBadge}>
            <Text style={styles.categoryText}>{item.category}</Text>
          </View>
        </View>
        <TouchableOpacity
          style={[
            styles.followButton,
            item.is_following && styles.followingButton,
          ]}
          onPress={() => handleFollowToggle(item)}
        >
          <Ionicons
            name={item.is_following ? 'checkmark' : 'add'}
            size={20}
            color={item.is_following ? '#10b981' : '#2563eb'}
          />
        </TouchableOpacity>
      </View>
      
      <Text style={styles.description} numberOfLines={2}>{item.description}</Text>
      
      <View style={styles.locationContainer}>
        <Ionicons name="location-outline" size={16} color="#64748b" />
        <Text style={styles.locationText}>{item.office_location}</Text>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>BigFirms</Text>
        <Text style={styles.headerSubtitle}>Follow infrastructure companies</Text>
      </View>

      <FlatList
        data={firms}
        renderItem={renderFirm}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        onEndReached={loadMore}
        onEndReachedThreshold={0.5}
        ListEmptyComponent={
          !loading ? (
            <View style={styles.emptyContainer}>
              <Ionicons name="business-outline" size={64} color="#cbd5e1" />
              <Text style={styles.emptyText}>No firms found</Text>
            </View>
          ) : null
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    padding: 24,
    paddingTop: 60,
    backgroundColor: '#ffffff',
    marginBottom: 8,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#64748b',
  },
  listContent: {
    padding: 16,
    paddingBottom: 100,
  },
  firmCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  firmHeader: {
    flexDirection: 'row',
    marginBottom: 12,
    alignItems: 'flex-start',
  },
  logo: {
    width: 56,
    height: 56,
    borderRadius: 12,
  },
  logoPlaceholder: {
    width: 56,
    height: 56,
    borderRadius: 12,
    backgroundColor: '#f1f5f9',
    justifyContent: 'center',
    alignItems: 'center',
  },
  firmInfo: {
    flex: 1,
    marginLeft: 12,
  },
  firmName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 6,
  },
  categoryBadge: {
    alignSelf: 'flex-start',
    backgroundColor: '#eff6ff',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  categoryText: {
    fontSize: 12,
    color: '#2563eb',
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  followButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#eff6ff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  followingButton: {
    backgroundColor: '#d1fae5',
  },
  description: {
    fontSize: 14,
    lineHeight: 20,
    color: '#64748b',
    marginBottom: 12,
  },
  locationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  locationText: {
    fontSize: 14,
    color: '#64748b',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 16,
    color: '#94a3b8',
    marginTop: 16,
  },
});
