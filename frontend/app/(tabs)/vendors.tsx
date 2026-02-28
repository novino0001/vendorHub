import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  TextInput,
  Image,
  RefreshControl,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import api from '@/utils/api';

interface Vendor {
  id: string;
  vendor_name: string;
  categories: string[];
  service_locations: string[];
  short_bio: string;
  avatar_base64?: string;
}

const CATEGORIES = ['All', 'civil', 'mechanical', 'electrical', 'transport'];

export default function VendorsScreen() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const loadVendors = async (pageNum = 1, category = selectedCategory, search = searchQuery) => {
    if (loading) return;
    
    try {
      setLoading(true);
      const params: any = { page: pageNum, per_page: 10 };
      if (category !== 'All') params.category = category;
      if (search) params.location = search;

      const response = await api.get('/vendors', { params });
      
      if (pageNum === 1) {
        setVendors(response.data.vendors);
      } else {
        setVendors((prev) => [...prev, ...response.data.vendors]);
      }
      
      setHasMore(response.data.vendors.length === 10);
      setPage(pageNum);
    } catch (error) {
      console.error('Error loading vendors:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVendors(1);
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadVendors(1);
    setRefreshing(false);
  };

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    loadVendors(1, category, searchQuery);
  };

  const handleSearch = () => {
    loadVendors(1, selectedCategory, searchQuery);
  };

  const loadMore = () => {
    if (hasMore && !loading) {
      loadVendors(page + 1, selectedCategory, searchQuery);
    }
  };

  const renderVendor = ({ item }: { item: Vendor }) => (
    <TouchableOpacity style={styles.vendorCard}>
      <View style={styles.vendorHeader}>
        {item.avatar_base64 ? (
          <Image source={{ uri: item.avatar_base64 }} style={styles.avatar} />
        ) : (
          <View style={styles.avatarPlaceholder}>
            <Ionicons name="person" size={32} color="#94a3b8" />
          </View>
        )}
        <View style={styles.vendorInfo}>
          <Text style={styles.vendorName}>{item.vendor_name}</Text>
          <View style={styles.categoriesContainer}>
            {item.categories.slice(0, 2).map((cat, index) => (
              <View key={index} style={styles.categoryBadge}>
                <Text style={styles.categoryText}>{cat}</Text>
              </View>
            ))}
            {item.categories.length > 2 && (
              <Text style={styles.moreText}>+{item.categories.length - 2}</Text>
            )}
          </View>
        </View>
      </View>
      
      <Text style={styles.bio} numberOfLines={2}>{item.short_bio}</Text>
      
      <View style={styles.locationContainer}>
        <Ionicons name="location-outline" size={16} color="#64748b" />
        <Text style={styles.locationText}>
          {item.service_locations[0]}
          {item.service_locations.length > 1 && ` +${item.service_locations.length - 1} more`}
        </Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Vendors</Text>
        <Text style={styles.headerSubtitle}>Discover contractors in your sector</Text>
      </View>

      <View style={styles.searchContainer}>
        <View style={styles.searchBar}>
          <Ionicons name="search" size={20} color="#64748b" />
          <TextInput
            style={styles.searchInput}
            placeholder="Search by location..."
            value={searchQuery}
            onChangeText={setSearchQuery}
            onSubmitEditing={handleSearch}
          />
        </View>
      </View>

      <View style={styles.filtersContainer}>
        <FlatList
          horizontal
          data={CATEGORIES}
          keyExtractor={(item) => item}
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoriesList}
          renderItem={({ item }) => (
            <TouchableOpacity
              style={[
                styles.categoryChip,
                selectedCategory === item && styles.categoryChipActive,
              ]}
              onPress={() => handleCategoryChange(item)}
            >
              <Text
                style={[
                  styles.categoryChipText,
                  selectedCategory === item && styles.categoryChipTextActive,
                ]}
              >
                {item}
              </Text>
            </TouchableOpacity>
          )}
        />
      </View>

      <FlatList
        data={vendors}
        renderItem={renderVendor}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        onEndReached={loadMore}
        onEndReachedThreshold={0.5}
        ListEmptyComponent={
          !loading ? (
            <View style={styles.emptyContainer}>
              <Ionicons name="people-outline" size={64} color="#cbd5e1" />
              <Text style={styles.emptyText}>No vendors found</Text>
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
  searchContainer: {
    padding: 16,
    backgroundColor: '#ffffff',
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
    borderRadius: 12,
    paddingHorizontal: 16,
    height: 48,
    gap: 12,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: '#1e293b',
  },
  filtersContainer: {
    backgroundColor: '#ffffff',
    paddingBottom: 16,
  },
  categoriesList: {
    paddingHorizontal: 16,
    gap: 8,
  },
  categoryChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#f1f5f9',
    marginRight: 8,
  },
  categoryChipActive: {
    backgroundColor: '#2563eb',
  },
  categoryChipText: {
    fontSize: 14,
    color: '#64748b',
    fontWeight: '600',
  },
  categoryChipTextActive: {
    color: '#ffffff',
  },
  listContent: {
    padding: 16,
    paddingBottom: 100,
  },
  vendorCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  vendorHeader: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  avatar: {
    width: 56,
    height: 56,
    borderRadius: 28,
  },
  avatarPlaceholder: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#f1f5f9',
    justifyContent: 'center',
    alignItems: 'center',
  },
  vendorInfo: {
    flex: 1,
    marginLeft: 12,
  },
  vendorName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 6,
  },
  categoriesContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  categoryBadge: {
    backgroundColor: '#eff6ff',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  categoryText: {
    fontSize: 12,
    color: '#2563eb',
    fontWeight: '600',
  },
  moreText: {
    fontSize: 12,
    color: '#64748b',
  },
  bio: {
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
