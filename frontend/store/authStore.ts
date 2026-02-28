import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../utils/api';

interface User {
  id: string;
  email: string;
  role: string;
  vendor_name?: string;
  phone?: string;
  gst_no?: string;
  revenue?: number;
  employee_count?: number;
  categories?: string[];
  service_locations?: string[];
  short_bio?: string;
  avatar_base64?: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  loadUser: () => Promise<void>;
  updateProfile: (data: any) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      const { access_token } = response.data;
      
      await AsyncStorage.setItem('access_token', access_token);
      
      // Fetch user data
      const userResponse = await api.get('/auth/me');
      await AsyncStorage.setItem('user_data', JSON.stringify(userResponse.data));
      
      set({ user: userResponse.data, isAuthenticated: true, isLoading: false });
    } catch (error: any) {
      console.error('Login error:', error.response?.data || error.message);
      throw error;
    }
  },

  signup: async (data: any) => {
    try {
      const response = await api.post('/auth/signup/vendor', data);
      const { access_token } = response.data;
      
      await AsyncStorage.setItem('access_token', access_token);
      
      // Fetch user data
      const userResponse = await api.get('/auth/me');
      await AsyncStorage.setItem('user_data', JSON.stringify(userResponse.data));
      
      set({ user: userResponse.data, isAuthenticated: true, isLoading: false });
    } catch (error: any) {
      console.error('Signup error:', error.response?.data || error.message);
      throw error;
    }
  },

  logout: async () => {
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('user_data');
    set({ user: null, isAuthenticated: false });
  },

  loadUser: async () => {
    try {
      const token = await AsyncStorage.getItem('access_token');
      if (!token) {
        set({ isLoading: false, isAuthenticated: false });
        return;
      }

      const userResponse = await api.get('/auth/me');
      set({ user: userResponse.data, isAuthenticated: true, isLoading: false });
    } catch (error) {
      console.error('Load user error:', error);
      await AsyncStorage.removeItem('access_token');
      await AsyncStorage.removeItem('user_data');
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  updateProfile: async (data: any) => {
    try {
      const response = await api.put('/vendors/me', data);
      const updatedUser = response.data;
      
      // Merge with existing user data
      set((state) => ({
        user: { ...state.user, ...updatedUser } as User,
      }));
      
      // Update AsyncStorage
      const userResponse = await api.get('/auth/me');
      await AsyncStorage.setItem('user_data', JSON.stringify(userResponse.data));
    } catch (error: any) {
      console.error('Update profile error:', error.response?.data || error.message);
      throw error;
    }
  },
}));
