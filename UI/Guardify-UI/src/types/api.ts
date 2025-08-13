// Shops (API)
export type ApiShop = {
    shop_id: string;
    name: string;
    address: string;
    company_id: string;
    creation_date: string;
  };
  
  // Events (API)
  export type ApiEvent = {
    event_id: string;
    event_datetime: string | null;
    event_timestamp: string | null;
    shop_id: string;
    shop_name: string | null;
    camera_id: string;
    camera_name: string | null;
    description: string | null;
    video_url: string | null;
    final_confidence?: number | null;
  };
  
  // Analysis (API)
  export type ApiEventAnalysis = {
    event_id: string;
    final_detection: boolean | null;
    final_confidence: number | null;
    decision_reasoning: string | null;
    analysis_timestamp: string | null;
  };
  
  // Event with embedded analysis (when backend supports it)
  export type ApiEventWithAnalysis = ApiEvent & {
    analysis?: ApiEventAnalysis | null;
  };

  // Login (API)
  export type ApiLoginResponse = {
    user_id: string;
    first_name: string;
    last_name: string;
    email: string;
  };
  
  // Camera (API)
export type ApiCamera = {
  camera_id: string;
  shop_id: string;
  camera_name: string | null;
};

// Company (API)  
export type ApiCompany = {
  company_id: string;
  company_name: string | null;
};

// User (API)
export type ApiUser = {
  user_id: string;
  first_name: string | null;
  last_name: string | null;
  email: string;
  password?: string | null;
};

// Stats (API) - matches StatsDTO
export type ApiStats = {
  events_per_day: Record<string, number>;
  events_by_hour: Record<string, number>;
  events_by_camera: Record<string, number>;
  events_by_category?: Record<string, number> | null;
};

// Request Bodies (API)
export type CreateEventRequest = {
  camera_id: string;
  description?: string;
  video_url?: string;
};

export type CreateCameraRequest = {
  camera_name: string;
};

export type CreateAnalysisRequest = {
  final_detection: boolean;
  final_confidence: number;
  decision_reasoning: string;
};

// Response aliases
export type ShopEventsResponse = ApiEvent[];
export type EventsResponse = ApiEvent[];
export type EventDetailsResponse = ApiEvent | ApiEventWithAnalysis;
export type UserShopsResponse = ApiShop[];
export type ShopCamerasResponse = ApiCamera[];
export type StatsResponse = ApiStats;
  