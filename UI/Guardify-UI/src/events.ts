
import type { Event } from './types';

export const events: Event[] = [
  { id: 'e1', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-04-03T09:33:29', description: 'Suspicious activity detected', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250403093329.mp4" },
  { id: 'e2', shopId: 'shop2', shopName: 'Haifa', date: '2025-04-03T09:36:59', description: 'Unusual behavior at exit', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250403093659.mp4" },
  { id: 'e3', shopId: 'shop3', shopName: 'Eilat', date: '2025-04-03T09:38:50', description: 'Person in a hurry', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250403093850.mp4" },
  { id: 'e4', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-04-03T09:39:54', description: 'Possible shoplifting behavior', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250403093954.mp4" },
  { id: 'e5', shopId: 'shop2', shopName: 'Haifa', date: '2025-04-03T09:53:19', description: 'Exit event captured', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250403095319.mp4" },
  { id: 'e6', shopId: 'shop3', shopName: 'Eilat', date: '2025-04-03T09:54:47', description: 'Individual behaving oddly', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250403095447.mp4" },
  { id: 'e7', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-04-03T09:58:03', description: 'Exit footage recorded', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250403095803.mp4" },
  { id: 'e8', shopId: 'shop2', shopName: 'Haifa', date: '2025-04-03T12:14:21', description: 'Customer leaving quickly', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250403121421.mp4" },
  { id: 'e9', shopId: 'shop3', shopName: 'Eilat', date: '2025-04-03T13:44:30', description: 'Suspicious package', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250403134430.mp4" },
  { id: 'e10', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-04-16T22:57:33', description: 'Late-night activity', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250416225733.mp4" },
  { id: 'e11', shopId: 'shop2', shopName: 'Haifa', date: '2025-04-16T22:58:17', description: 'Exit triggered alert', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250416225817.mp4" },
  { id: 'e12', shopId: 'shop3', shopName: 'Eilat', date: '2025-04-16T23:02:33', description: 'Motion near door', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250416230233.mp4" },
  { id: 'e13', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-04-16T23:06:55', description: 'Individual leaving in a rush', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250416230655.mp4" },
  { id: 'e14', shopId: 'shop2', shopName: 'Haifa', date: '2025-04-16T23:11:03', description: 'Potential shoplifting event', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250416231103.mp4" },
  { id: 'e15', shopId: 'shop3', shopName: 'Eilat', date: '2025-04-16T23:12:57', description: 'Exit camera triggered', cameraId: 'cam1', cameraName: 'Exit Camera', videoUrl: "/videos/fixed/exit1_20250416231257.mp4" },
  
  { id: 'e16', shopId: 'shop2', shopName: 'Haifa', date: '2025-04-03T13:06:06', description: 'Face recognition alert', cameraId: 'cam7', cameraName: 'Face Recognition', videoUrl: "/videos/fixed/face recognition_20250403130606.mp4" },
  { id: 'e17', shopId: 'shop3', shopName: 'Eilat', date: '2025-04-03T13:09:12', description: 'Face match detected', cameraId: 'cam7', cameraName: 'Face Recognition', videoUrl: "/videos/fixed/face recognition_20250403130912.mp4" },
  { id: 'e18', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-04-16T22:56:58', description: 'Face recognition suspicious match', cameraId: 'cam7', cameraName: 'Face Recognition', videoUrl: "/videos/fixed/face recognition_20250416225658.mp4" },
  { id: 'e19', shopId: 'shop2', shopName: 'Haifa', date: '2025-04-16T23:03:11', description: 'Face recognition triggered', cameraId: 'cam7', cameraName: 'Face Recognition', videoUrl: "/videos/fixed/face recognition_20250416230311.mp4" },
  { id: 'e20', shopId: 'shop3', shopName: 'Eilat', date: '2025-04-16T23:22:52', description: 'Face recognition identified person of interest', cameraId: 'cam7', cameraName: 'Face Recognition', videoUrl: "/videos/fixed/face recognition_20250416232252.mp4" },

  { id: 'e21', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-04-03T12:47:40', description: 'Cash register activity recorded', cameraId: 'cam2', cameraName: 'Kupa 1', videoUrl: "/videos/fixed/Kupa 1_20250403124740.mp4" },
  { id: 'e22', shopId: 'shop2', shopName: 'Haifa', date: '2025-04-03T12:50:06', description: 'Checkout motion detected', cameraId: 'cam2', cameraName: 'Kupa 1', videoUrl: "/videos/fixed/Kupa 1_20250403125006.mp4" },
  { id: 'e23', shopId: 'shop3', shopName: 'Eilat', date: '2025-04-03T13:03:44', description: 'Customer scanning items', cameraId: 'cam2', cameraName: 'Kupa 1', videoUrl: "/videos/fixed/Kupa 1_20250403130344.mp4" },
  { id: 'e24', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-04-16T22:45:57', description: 'Unusual checkout behavior', cameraId: 'cam2', cameraName: 'Kupa 1', videoUrl: "/videos/fixed/Kupa 1_20250416224557.mp4" },
  { id: 'e25', shopId: 'shop2', shopName: 'Haifa', date: '2025-04-16T22:55:05', description: 'Cash register interaction', cameraId: 'cam2', cameraName: 'Kupa 1', videoUrl: "/videos/fixed/Kupa 1_20250416225505.mp4" },
  { id: 'e26', shopId: 'shop3', shopName: 'Eilat', date: '2025-04-16T22:55:21', description: 'Suspicious behavior at checkout', cameraId: 'cam2', cameraName: 'Kupa 1', videoUrl: "/videos/fixed/Kupa 1_20250416225521.mp4" },
  { id: 'e27', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-04-16T23:35:12', description: 'Cash drawer opened', cameraId: 'cam2', cameraName: 'Kupa 1', videoUrl: "/videos/fixed/Kupa 1_20250416233512.mp4" },

  { id: 'e28', shopId: 'shop2', shopName: 'Haifa', date: '2025-04-16T23:05:08', description: 'Kupa 2 activity detected', cameraId: 'cam3', cameraName: 'Kupa 2', videoUrl: "/videos/fixed/Kupa 2_20250416230508.mp4" },

  { id: 'e29', shopId: 'shop3', shopName: 'Eilat', date: '2025-04-03T13:17:46', description: 'Money transfer logged', cameraId: 'cam4', cameraName: 'Money 1', videoUrl: "/videos/fixed/Money 1_20250403131746.mp4" },

  { id: 'e30', shopId: 'shop1', shopName: 'Tel Aviv', date: '2025-04-03T09:47:22', description: 'Child near sweets shelf', cameraId: 'cam5', cameraName: 'Sweets 1', videoUrl: "/videos/fixed/Sweets 1_20250403094722.mp4" },
  { id: 'e31', shopId: 'shop2', shopName: 'Haifa', date: '2025-04-03T12:32:07', description: 'Person taking item from sweets shelf', cameraId: 'cam5', cameraName: 'Sweets 1', videoUrl: "/videos/fixed/Sweets 1_20250403123207.mp4" }
];
