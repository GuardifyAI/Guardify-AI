import { AlertTriangle, CheckCircle } from 'lucide-react';

export interface StatusInfo {
  label: string;
  color: string;
  bgColor: string;
  icon: typeof AlertTriangle | typeof CheckCircle;
}

export const getStatusInfo = (detection: boolean, confidence: number): StatusInfo => {
  if (detection) {
    if (confidence >= 80) {
      return {
        label: 'INCIDENT',
        color: 'text-red-500',
        bgColor: 'bg-red-500',
        icon: AlertTriangle
      };
    } else {
      return {
        label: 'SUSPICIOUS',
        color: 'text-yellow-500',
        bgColor: 'bg-yellow-500',
        icon: AlertTriangle
      };
    }
  } else {
    return {
      label: 'SAFE',
      color: 'text-green-600',
      bgColor: 'bg-green-600',
      icon: CheckCircle
    };
  }
};