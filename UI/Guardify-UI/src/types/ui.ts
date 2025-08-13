// Shops (UI)
export type Shop = {
    id: string;
    name: string;
    incidents: number;
  };
  
  // Events (UI)
  export type EventAnalysis = {
    finalDetection: boolean;
    finalConfidence: number;
    decisionReasoning: string;
    analysisTimestamp: string;
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
    analysis: EventAnalysis | null;
  };
  
  // Auth + misc (UI)
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
  };
  
  export interface LoginResponse extends Omit<User, 'email'> {
    token: string;
  }
  
  // Camera (UI)
  export type Camera = {
    id: string;
    shopId: string;
    name: string;
  };

  // Company (UI)
  export type Company = {
    id: string;
    name: string;
  };

  // Stats (UI) - for display purposes  
  export type Stats = {
    eventsByCamera: Record<string, number>;
    eventsByCategory?: Record<string, number>;
    eventsByHour: Record<string, number>;
    eventsPerDay: Record<string, number>;
  };