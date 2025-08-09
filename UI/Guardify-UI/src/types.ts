// UI Shop type (what components expect)
export type Shop = {
  id: string;
  name: string;
  incidents: number;
};

// API Shop type (matches backend response)
export type ApiShop = {
  shop_id: string;
  name: string;
  address: string;
  company_id: string;
  creation_date: string;
};


export type Event = {
  id: string;
  shopId: string;
  shopName: string;
  date: string;
  description: string;
  cameraId: string;
  cameraName: string;
  videoUrl: string;
  analysis: EventAnalysis;
};

// Add this new type for shop events API response (matches your actual API)
export type ApiEvent = {
  event_id: string;
  event_datetime: string;
  event_timestamp: string;
  shop_id: string;
  shop_name: string;
  camera_id: string;
  camera_name: string;
  description: string;
  video_url: string;
};

export type EventAnalysis = {
  final_detection: boolean;
  final_confidence: number;
  decision_reasoning: string;
  analysis_timestamp: string;
};


// Authentication-related types
export interface User {
  userId: string;
  firstName: string;
  lastName: string;
  email?: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}

export type SidebarProps = {
  shops: Shop[];
  selectedShop: string | null;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  setSelectedShop: (shopId: string | null) => void;
}

// Login request/response types
export interface LoginResponse extends Omit<User, 'email'> {
  token: string;
}

export type StatsResponse = {
  events_by_camera: Record<string, number>;
  events_by_category: Record<string, number>;
  events_by_hour: Record<string, number>;
  events_per_day: Record<string, number>;
};


// Add type for the API response
export type UserShopsResponse = ApiShop[];
export type ShopEventsResponse = ApiEvent[];
