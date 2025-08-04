import type { Event, Shop } from '../types';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API error ${res.status}: ${errorText}`);
  }
  return res.json();
}

export async function fetchShops(): Promise<Shop[]> {
  const res = await fetch('/shops');
  return handleResponse(res);
}

export async function fetchEventsByShop(shopId: string): Promise<Event[]> {
  const res = await fetch(`/shops/${shopId}/events`);
  return handleResponse(res);
}

export async function fetchAllEvents(): Promise<Event[]> {
  const res = await fetch(`/events`);
  return handleResponse(res);
}

export async function fetchShopStats(shopId: string) {
  const res = await fetch(`/shops/${shopId}/stats`);
  return handleResponse(res);
}

export async function fetchGlobalStats() {
  const res = await fetch(`/stats`);
  return handleResponse(res);
}

export async function fetchEvent(eventId: string): Promise<Event> {
  const res = await fetch(`/events/${eventId}`);
  return handleResponse(res);
}

export async function fetchAnalysis(eventId: string) {
  const res = await fetch(`/analysis/${eventId}`);
  return handleResponse(res);
}
