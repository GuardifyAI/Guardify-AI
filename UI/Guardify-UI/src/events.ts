export const events = [
  {
    id: 'e1',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-04-03T09:33:29',
    description: 'Suspicious activity detected',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250403093329.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 0.5774,
      decisionReasoning: "Exit behavior abnormal.",
      analysisTimestamp: '2025-04-03T09:34:00'
    }
  },
  {
    id: 'e2',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-04-03T09:36:59',
    description: 'Unusual behavior at exit',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250403093659.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 0.524,
      decisionReasoning: "Face match with known offender.",
      analysisTimestamp: '2025-04-03T09:37:42'
    }
  },
  {
    id: 'e3',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-04-03T09:38:50',
    description: 'Person in a hurry',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250403093850.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 62.69,
      decisionReasoning: "Hand near pocket during exit.",
      analysisTimestamp: '2025-04-03T09:39:24'
    }
  },
  {
    id: 'e4',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-04-03T09:39:54',
    description: 'Possible shoplifting behavior',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250403093954.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 96.49,
      decisionReasoning: "Checkout time exceeded average duration.",
      analysisTimestamp: '2025-04-03T09:40:04'
    }
  },
  {
    id: 'e5',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-04-03T09:53:19',
    description: 'Exit event captured',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250403095319.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 97.03,
      decisionReasoning: "Face match with known offender.",
      analysisTimestamp: '2025-04-03T09:53:35'
    }
  },
  {
    id: 'e6',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-04-03T09:54:47',
    description: 'Individual behaving oddly',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250403095447.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 67.4,
      decisionReasoning: "Suspicious hand movement detected.",
      analysisTimestamp: '2025-04-03T09:55:35'
    }
  },
  {
    id: 'e7',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-04-03T09:58:03',
    description: 'Exit footage recorded',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250403095803.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 94.52,
      decisionReasoning: "Multiple entries without purchase.",
      analysisTimestamp: '2025-04-03T09:58:26'
    }
  },
  {
    id: 'e8',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-04-03T12:14:21',
    description: 'Customer leaving quickly',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250403121421.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 72.24,
      decisionReasoning: "Multiple entries without purchase.",
      analysisTimestamp: '2025-04-03T12:14:35'
    }
  },
  {
    id: 'e9',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-04-03T13:44:30',
    description: 'Suspicious package',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250403134430.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 61.96,
      decisionReasoning: "Unexpected object interaction detected.",
      analysisTimestamp: '2025-04-03T13:45:15'
    }
  },
  {
    id: 'e10',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-04-16T22:57:33',
    description: 'Late-night activity',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250416225733.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 56.75,
      decisionReasoning: "Face match with known offender.",
      analysisTimestamp: '2025-04-16T22:58:00'
    }
  },
  {
    id: 'e11',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-04-16T22:58:17',
    description: 'Exit triggered alert',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250416225817.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 99.26,
      decisionReasoning: "Face match with known offender.",
      analysisTimestamp: '2025-04-16T22:58:31'
    }
  },
  {
    id: 'e12',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-04-16T23:02:33',
    description: 'Motion near door',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250416230233.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 55.1,
      decisionReasoning: "Person left with unseen item.",
      analysisTimestamp: '2025-04-16T23:02:49'
    }
  },
  {
    id: 'e13',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-04-16T23:06:55',
    description: 'Individual leaving in a rush',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250416230655.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 85.49,
      decisionReasoning: "Person left with unseen item.",
      analysisTimestamp: '2025-04-16T23:07:15'
    }
  },
  {
    id: 'e14',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-04-16T23:11:03',
    description: 'Potential shoplifting event',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250416231103.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 97.07,
      decisionReasoning: "Standard behavior; no anomalies.",
      analysisTimestamp: '2025-04-16T23:12:02'
    }
  },
  {
    id: 'e15',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-04-16T23:12:57',
    description: 'Exit camera triggered',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250416231257.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 70.7,
      decisionReasoning: "Hand near pocket during exit.",
      analysisTimestamp: '2025-04-16T23:13:51'
    }
  },
  {
    id: 'e16',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-04-03T13:06:06',
    description: 'Face recognition alert',
    cameraId: 'cam1',
    cameraName: 'Face Recognition',
    videoUrl: '/videos/fixed/face recognition_20250403130606.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 81.0,
      decisionReasoning: "Unexpected object interaction detected.",
      analysisTimestamp: '2025-04-03T13:06:54'
    }
  },
  {
    id: 'e17',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-04-03T13:09:12',
    description: 'Face match detected',
    cameraId: 'cam1',
    cameraName: 'Face Recognition',
    videoUrl: '/videos/fixed/face recognition_20250403130912.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 79.14,
      decisionReasoning: "Facial expressions suggested stress.",
      analysisTimestamp: '2025-04-03T13:09:25'
    }
  },
  {
    id: 'e18',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-04-16T22:56:58',
    description: 'Face recognition suspicious match',
    cameraId: 'cam1',
    cameraName: 'Face Recognition',
    videoUrl: '/videos/fixed/face recognition_20250416225658.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 77.0,
      decisionReasoning: "Exit behavior abnormal.",
      analysisTimestamp: '2025-04-16T22:57:19'
    }
  },
  {
    id: 'e19',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-04-16T23:03:11',
    description: 'Face recognition triggered',
    cameraId: 'cam1',
    cameraName: 'Face Recognition',
    videoUrl: '/videos/fixed/face recognition_20250416230311.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 52.14,
      decisionReasoning: "Facial expressions suggested stress.",
      analysisTimestamp: '2025-04-16T23:03:22'
    }
  },
  {
    id: 'e20',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-04-16T23:22:52',
    description: 'Face recognition identified person of interest',
    cameraId: 'cam1',
    cameraName: 'Face Recognition',
    videoUrl: '/videos/fixed/face recognition_20250416232252.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 79.72,
      decisionReasoning: "Multiple entries without purchase.",
      analysisTimestamp: '2025-04-16T23:23:16'
    }
  },
  {
    id: 'e21',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-04-03T12:47:40',
    description: 'Cash register activity recorded',
    cameraId: 'cam1',
    cameraName: 'Kupa 1',
    videoUrl: '/videos/fixed/Kupa 1_20250403124740.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 91.03,
      decisionReasoning: "Checkout time exceeded average duration.",
      analysisTimestamp: '2025-04-03T12:48:10'
    }
  },
  {
    id: 'e22',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-04-03T12:50:06',
    description: 'Checkout motion detected',
    cameraId: 'cam1',
    cameraName: 'Kupa 1',
    videoUrl: '/videos/fixed/Kupa 1_20250403125006.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 98.64,
      decisionReasoning: "Face match with known offender.",
      analysisTimestamp: '2025-04-03T12:50:33'
    }
  },
  {
    id: 'e23',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-04-03T13:03:44',
    description: 'Customer scanning items',
    cameraId: 'cam1',
    cameraName: 'Kupa 1',
    videoUrl: '/videos/fixed/Kupa 1_20250403130344.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 70.0,
      decisionReasoning: "Unexpected object interaction detected.",
      analysisTimestamp: '2025-04-03T13:03:56'
    }
  },
  {
    id: 'e24',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-04-16T22:45:57',
    description: 'Unusual checkout behavior',
    cameraId: 'cam1',
    cameraName: 'Kupa 1',
    videoUrl: '/videos/fixed/Kupa 1_20250416224557.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 91.97,
      decisionReasoning: "Suspicious hand movement detected.",
      analysisTimestamp: '2025-04-16T22:46:34'
    }
  },
  {
    id: 'e25',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-04-16T22:55:05',
    description: 'Cash register interaction',
    cameraId: 'cam1',
    cameraName: 'Kupa 1',
    videoUrl: '/videos/fixed/Kupa 1_20250416225505.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 96.1,
      decisionReasoning: "Suspicious hand movement detected.",
      analysisTimestamp: '2025-04-16T22:55:22'
    }
  },
  {
    id: 'e26',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-04-16T22:55:21',
    description: 'Suspicious behavior at checkout',
    cameraId: 'cam1',
    cameraName: 'Kupa 1',
    videoUrl: '/videos/fixed/Kupa 1_20250416225521.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 72.72,
      decisionReasoning: "Suspicious hand movement detected.",
      analysisTimestamp: '2025-04-16T22:55:36'
    }
  },
  {
    id: 'e27',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-04-16T23:35:12',
    description: 'Cash drawer opened',
    cameraId: 'cam1',
    cameraName: 'Kupa 1',
    videoUrl: '/videos/fixed/Kupa 1_20250416233512.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 75.66,
      decisionReasoning: "Suspicious hand movement detected.",
      analysisTimestamp: '2025-04-16T23:35:39'
    }
  },
  {
    id: 'e28',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-04-16T23:05:08',
    description: 'Kupa 2 activity detected',
    cameraId: 'cam1',
    cameraName: 'Kupa 2',
    videoUrl: '/videos/fixed/Kupa 2_20250416230508.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 74.77,
      decisionReasoning: "Checkout time exceeded average duration.",
      analysisTimestamp: '2025-04-16T23:05:52'
    }
  },
  {
    id: 'e29',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-04-03T13:17:46',
    description: 'Employee takes money from the cash register without authorization',
    cameraId: 'cam1',
    cameraName: 'Money 1',
    videoUrl: '/videos/fixed/Money 1_20250403131746.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 83.17,
      decisionReasoning: "Employee is seen removing cash from the register without performing any transaction or interacting with a customer.",
      analysisTimestamp: '2025-04-03T13:18:19'
    }
  },
  {
    id: 'e30',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-04-03T09:47:22',
    description: 'Child near sweets shelf',
    cameraId: 'cam1',
    cameraName: 'Sweets 1',
    videoUrl: '/videos/fixed/Sweets 1_20250403094722.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 55.62,
      decisionReasoning: "Exit behavior abnormal.",
      analysisTimestamp: '2025-04-03T09:47:36'
    }
  },
  {
    id: 'e31',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-04-03T12:32:07',
    description: 'Person taking item from sweets shelf',
    cameraId: 'cam1',
    cameraName: 'Sweets 1',
    videoUrl: '/videos/fixed/Sweets 1_20250403123207.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 99.79,
      decisionReasoning: "Facial expressions suggested stress.",
      analysisTimestamp: '2025-04-03T12:32:17'
    }
  },
  {
    id: 'e32',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-05-02T10:15:00',
    description: 'Suspicious activity detected',
    cameraId: 'cam1',
    cameraName: 'Kupa 1',
    videoUrl: '/videos/fixed/Kupa 1_20250502101500.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 58.12,
      decisionReasoning: 'Unusual checkout behavior.',
      analysisTimestamp: '2025-05-02T10:15:30'
    }
  },
  {
    id: 'e33',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-05-03T11:20:00',
    description: 'Unusual behavior at exit',
    cameraId: 'cam1',
    cameraName: 'Face Recognition',
    videoUrl: '/videos/fixed/face recognition_20250503112000.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 62.45,
      decisionReasoning: 'Face match with known offender.',
      analysisTimestamp: '2025-05-03T11:20:30'
    }
  },
  {
    id: 'e34',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-05-04T12:25:00',
    description: 'Person in a hurry',
    cameraId: 'cam1',
    cameraName: 'Sweets 1',
    videoUrl: '/videos/fixed/Sweets 1_20250504122500.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 67.89,
      decisionReasoning: 'Hand near pocket during exit.',
      analysisTimestamp: '2025-05-04T12:25:30'
    }
  },
  {
    id: 'e35',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-05-05T13:30:00',
    description: 'Possible shoplifting behavior',
    cameraId: 'cam1',
    cameraName: 'Kupa 2',
    videoUrl: '/videos/fixed/Kupa 2_20250505133000.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 91.23,
      decisionReasoning: 'Checkout time exceeded average duration.',
      analysisTimestamp: '2025-05-05T13:30:30'
    }
  },
  {
    id: 'e36',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-05-06T14:35:00',
    description: 'Exit event captured',
    cameraId: 'cam1',
    cameraName: 'Money 1',
    videoUrl: '/videos/fixed/Money 1_20250506143500.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 73.56,
      decisionReasoning: 'Employee is seen removing cash from the register.',
      analysisTimestamp: '2025-05-06T14:35:30'
    }
  },
  {
    id: 'e37',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-05-07T15:40:00',
    description: 'Individual behaving oddly',
    cameraId: 'cam1',
    cameraName: 'Exit Camera',
    videoUrl: '/videos/fixed/exit1_20250507154000.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 85.67,
      decisionReasoning: 'Suspicious hand movement detected.',
      analysisTimestamp: '2025-05-07T15:40:30'
    }
  },
  {
    id: 'e38',
    shopId: 'shop1',
    shopName: 'Tel Aviv',
    date: '2025-05-08T16:45:00',
    description: 'Exit footage recorded',
    cameraId: 'cam1',
    cameraName: 'Kupa 1',
    videoUrl: '/videos/fixed/Kupa 1_20250508164500.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 59.34,
      decisionReasoning: 'Multiple entries without purchase.',
      analysisTimestamp: '2025-05-08T16:45:30'
    }
  },
  {
    id: 'e39',
    shopId: 'shop2',
    shopName: 'Haifa',
    date: '2025-05-09T17:50:00',
    description: 'Customer leaving quickly',
    cameraId: 'cam1',
    cameraName: 'Sweets 1',
    videoUrl: '/videos/fixed/Sweets 1_20250509175000.mp4',
    analysis: {
      finalDetection: true,
      finalConfidence: 77.21,
      decisionReasoning: 'Multiple entries without purchase.',
      analysisTimestamp: '2025-05-09T17:50:30'
    }
  },
  {
    id: 'e40',
    shopId: 'shop3',
    shopName: 'Eilat',
    date: '2025-05-10T18:55:00',
    description: 'Suspicious package',
    cameraId: 'cam1',
    cameraName: 'Face Recognition',
    videoUrl: '/videos/fixed/face recognition_20250510185500.mp4',
    analysis: {
      finalDetection: false,
      finalConfidence: 61.11,
      decisionReasoning: 'Unexpected object interaction detected.',
      analysisTimestamp: '2025-05-10T18:55:30'
    }
  },
];
