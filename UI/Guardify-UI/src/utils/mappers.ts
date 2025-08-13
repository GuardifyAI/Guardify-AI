// src/utils/mappers.ts
import type { 
  ApiShop, 
  ApiEventWithAnalysis, 
  ApiEventAnalysis, 
  ApiEvent, 
  ApiCamera, 
  ApiCompany, 
  ApiUser, 
  ApiStats,
  ApiLoginResponse
} from '../types/api';
import type { 
  Shop, 
  Event, 
  EventAnalysis, 
  Camera, 
  Company, 
  User, 
  Stats 
} from '../types/ui';

// Shops
export const mapApiShop = (s: ApiShop): Shop => ({
  id: s.shop_id,
  name: s.name,
  incidents: 0, // compute later
});

// Analysis
export const mapApiAnalysis = (a?: ApiEventAnalysis | null): EventAnalysis => ({
  finalDetection: !!(a?.final_detection ?? false),
  finalConfidence: Number(a?.final_confidence ?? 0),
  decisionReasoning: a?.decision_reasoning ?? '',
  analysisTimestamp: a?.analysis_timestamp ?? '',
});

// Events (works with or without embedded analysis)
export const mapApiEvent = (e: ApiEvent | ApiEventWithAnalysis): Event => ({
  id: e.event_id,
  shopId: e.shop_id,
  shopName: e.shop_name ?? '',
  date: e.event_datetime ?? e.event_timestamp ?? '',
  description: e.description ?? '',
  cameraId: e.camera_id,
  cameraName: e.camera_name ?? '',
  videoUrl: e.video_url ?? '',
  // prefer nested analysis; if missing or null, return null
  analysis: (() => {
    if ('analysis' in e && e.analysis) return mapApiAnalysis(e.analysis);
    if ('analysis' in e && e.analysis === null) return null;
    // fallback path for events without analysis field at all
    return {
      finalDetection: false,
      finalConfidence: Number((e as ApiEvent).final_confidence ?? 0),
      decisionReasoning: '',
      analysisTimestamp: '',
    };
  })(),
});

// Cameras
export const mapApiCamera = (c: ApiCamera): Camera => ({
  id: c.camera_id,
  shopId: c.shop_id,
  name: c.camera_name ?? '',
});

// Companies
export const mapApiCompany = (c: ApiCompany): Company => ({
  id: c.company_id,
  name: c.company_name ?? '',
});

// Users
export const mapApiUser = (u: ApiUser): User => ({
  userId: u.user_id,
  firstName: u.first_name ?? '',
  lastName: u.last_name ?? '',
  email: u.email,
});

// Login Response
export const mapApiLoginResponse = (response: ApiLoginResponse): User => ({
  userId: response.userId,
  firstName: response.firstName,
  lastName: response.lastName,
  email: '', // Email will be added separately since backend doesn't return it
});

// Stats
export const mapApiStats = (s: ApiStats): Stats => ({
  eventsByCamera: s.events_by_camera,
  eventsByCategory: s.events_by_category ?? undefined,
  eventsByHour: s.events_by_hour,
  eventsPerDay: s.events_per_day,
});

// Array mappers for convenience
export const mapApiShops = (shops: ApiShop[]): Shop[] => 
  shops.map(mapApiShop);

export const mapApiEvents = (events: (ApiEvent | ApiEventWithAnalysis)[]): Event[] => 
  events.map(mapApiEvent);

export const mapApiCameras = (cameras: ApiCamera[]): Camera[] => 
  cameras.map(mapApiCamera);

export const mapApiCompanies = (companies: ApiCompany[]): Company[] => 
  companies.map(mapApiCompany);

