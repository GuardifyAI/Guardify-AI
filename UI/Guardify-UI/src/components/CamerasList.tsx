import React, { useState, useEffect } from 'react';
import { Camera, Play, Square, Clock, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { shopsService } from '../services/shops';
import { mapApiCameras } from '../utils/mappers';
import type { Camera as CameraType } from '../types/ui';

interface CamerasListProps {
  shopId: string;
  shopName: string;
}

interface RecordingStatus {
  camera_name: string;
  started_at: number;
  duration: number;
}

interface CameraWithStatus extends CameraType {
  isRecording: boolean;
  recordingStartedAt?: number;
}

export default function CamerasList({ shopId, shopName }: CamerasListProps) {
  const [cameras, setCameras] = useState<CameraWithStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recordingStatuses, setRecordingStatuses] = useState<RecordingStatus[]>([]);
  const [operationInProgress, setOperationInProgress] = useState<string | null>(null);
  const { token } = useAuth();

  // Fetch cameras for the shop
  const fetchCameras = async () => {
    if (!token) return;

    try {
      setError(null);
      const response = await shopsService.getShopCameras(shopId, token);
      
      if (response.result && !response.errorMessage) {
        const mappedCameras = mapApiCameras(response.result);
        setCameras(mappedCameras.map(camera => ({ ...camera, isRecording: false })));
      } else {
        setError(response.errorMessage || 'Failed to fetch cameras');
      }
    } catch (err) {
      setError('Failed to load cameras');
      console.error('Error fetching cameras:', err);
    }
  };

  // Fetch recording status for the shop
  const fetchRecordingStatus = async () => {
    if (!token) return;

    try {
      const response = await shopsService.getRecordingStatus(shopId, token);
      
      if (response.result && !response.errorMessage) {
        setRecordingStatuses(response.result);
      } else {
        setRecordingStatuses([]);
      }
    } catch (err) {
      setRecordingStatuses([]);
      console.error('Error fetching recording status:', err);
    }
  };

  // Update cameras with recording status
  useEffect(() => {
    setCameras(prevCameras => 
      prevCameras.map(camera => {
        const recordingStatus = recordingStatuses.find(
          status => status.camera_name === camera.name
        );
        return {
          ...camera,
          isRecording: !!recordingStatus,
          recordingStartedAt: recordingStatus?.started_at
        };
      })
    );
  }, [recordingStatuses]);

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchCameras(), fetchRecordingStatus()]);
      setLoading(false);
    };

    loadData();
  }, [shopId, token]);

  // Refresh recording status periodically
  useEffect(() => {
    const interval = setInterval(fetchRecordingStatus, 5000); // Check every 5 seconds
    return () => clearInterval(interval);
  }, [shopId, token]);

  const handleStartRecording = async (cameraName: string) => {
    if (!token || operationInProgress) return;

    setOperationInProgress(cameraName);
    try {
      const response = await shopsService.startRecording(shopId, cameraName, 30, token);
      
      if (response.result && !response.errorMessage) {
        // Refresh status after starting
        await fetchRecordingStatus();
      } else {
        alert(`Failed to start recording: ${response.errorMessage}`);
      }
    } catch (err) {
      alert('Failed to start recording');
      console.error('Error starting recording:', err);
    } finally {
      setOperationInProgress(null);
    }
  };

  const handleStopRecording = async (cameraName: string) => {
    if (!token || operationInProgress) return;

    setOperationInProgress(cameraName);
    try {
      const response = await shopsService.stopRecording(shopId, cameraName, token);
      
      if (response.result && !response.errorMessage) {
        // Refresh status after stopping
        await fetchRecordingStatus();
      } else {
        alert(`Failed to stop recording: ${response.errorMessage}`);
      }
    } catch (err) {
      alert('Failed to stop recording');
      console.error('Error stopping recording:', err);
    } finally {
      setOperationInProgress(null);
    }
  };

  const formatRecordingTime = (startedAt: number) => {
    const elapsed = Math.floor((Date.now() - startedAt * 1000) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-primary-500 mr-2" />
          <span className="text-gray-600">Loading cameras...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
        <div className="text-center py-8">
          <div className="text-red-500 mb-2">Failed to load cameras</div>
          <div className="text-gray-600 text-sm">{error}</div>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Cameras in {shopName}
        </h3>
        <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
          {cameras.length} camera{cameras.length !== 1 ? 's' : ''}
        </span>
      </div>

      {cameras.length === 0 ? (
        <div className="text-center py-8">
          <Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <div className="text-gray-500">No cameras found in this shop</div>
        </div>
      ) : (
        <div className="space-y-4">
          {cameras.map((camera) => (
            <div 
              key={camera.id} 
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                  <Camera className="w-5 h-5 text-gray-600" />
                </div>
                <div>
                  <div className="font-medium text-gray-900">{camera.name}</div>
                  <div className="text-sm text-gray-500">Camera ID: {camera.id}</div>
                  {camera.isRecording && camera.recordingStartedAt && (
                    <div className="flex items-center text-sm text-green-600 mt-1">
                      <Clock className="w-4 h-4 mr-1" />
                      Recording: {formatRecordingTime(camera.recordingStartedAt)}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleStartRecording(camera.name)}
                  disabled={camera.isRecording || operationInProgress === camera.name}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    camera.isRecording || operationInProgress === camera.name
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-green-500 text-white hover:bg-green-600 shadow-sm hover:shadow-md'
                  }`}
                >
                  {operationInProgress === camera.name ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Play className="w-4 h-4" />
                  )}
                  <span>Start Record</span>
                </button>

                <button
                  onClick={() => handleStopRecording(camera.name)}
                  disabled={!camera.isRecording || operationInProgress === camera.name}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    !camera.isRecording || operationInProgress === camera.name
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-red-500 text-white hover:bg-red-600 shadow-sm hover:shadow-md'
                  }`}
                >
                  {operationInProgress === camera.name ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Square className="w-4 h-4" />
                  )}
                  <span>Stop Record</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
