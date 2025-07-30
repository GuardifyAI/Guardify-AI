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

export type User = {
  id: string;
  name: string;
  role: 'manager' | 'guard';
};

export type SidebarProps = {
  shops: Shop[];
  selectedShop: string | null;
  activeTab: string;
  setActiveTab: (tab: string) => void;
  setSelectedShop: (shopId: string | null) => void;
};
