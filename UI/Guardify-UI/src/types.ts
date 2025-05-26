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
};

export type User = {
  id: string;
  name: string;
  role: 'manager' | 'guard';
};