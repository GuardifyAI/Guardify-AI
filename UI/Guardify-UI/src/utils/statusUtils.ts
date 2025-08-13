import { AlertTriangle, CheckCircle } from 'lucide-react';
import type { EventAnalysis } from '../types/ui';

export interface StatusInfo {
  label: string;
  color: string;
  bgColor: string;
  icon: typeof AlertTriangle | typeof CheckCircle;
}

export const getStatusInfo = (detection: boolean, confidence: number): StatusInfo => {
  if (detection) {
    if (confidence >= 0.8) {  // 80% confidence threshold (0.8 in 0-1 range)
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

export const getEventStatusInfo = (analysis: EventAnalysis | null | undefined): StatusInfo => {
  // Check if analysis exists and has valid data
  if (analysis && 
      analysis.finalDetection !== undefined && 
      analysis.finalConfidence !== undefined) {
    return getStatusInfo(analysis.finalDetection, analysis.finalConfidence);
  }
  
  // Return "Not Provided" status for null/undefined analysis
  return {
    label: 'Not Provided',
    color: 'text-gray-500',
    bgColor: 'bg-gray-100',
    icon: AlertTriangle
  };
};