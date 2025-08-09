export type Shop = {
  id: string;
  name: string;
  incidents: number;
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