import { useState, useEffect } from 'react';
import { Camera, Loader2, Plus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { cameraService } from '../services/cameras';
import { mapApiCameras } from '../utils/mappers';
import type { Camera as CameraType } from '../types/ui';
import AddCameraModal from './cameras/AddCameraModal';
import CameraItem from './cameras/CameraItem';

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
  const [showAddCameraModal, setShowAddCameraModal] = useState(false);
  const { token } = useAuth();

  // Fetch cameras for the shop
  const fetchCameras = async () => {
    if (!token) return;

    try {
      setError(null);
      const response = await cameraService.getShopCameras(shopId, token);
      
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
      const response = await cameraService.getRecordingStatus(shopId, token);
      
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
      const response = await cameraService.startRecording(shopId, cameraName, 30, token);
      
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
      const response = await cameraService.stopRecording(shopId, cameraName, token);
      
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

  const handleCameraAdded = (newCamera: CameraType) => {
    const cameraWithStatus: CameraWithStatus = {
      ...newCamera,
      isRecording: false
    };
    setCameras(prev => [...prev, cameraWithStatus]);
  };

  const handleDeleteCamera = (cameraId: string) => {
    setCameras(prev => prev.filter(camera => camera.id !== cameraId));
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
        <div className="flex items-center space-x-3">
          <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
            {cameras.length} camera{cameras.length !== 1 ? 's' : ''}
          </span>
          <button
            onClick={() => setShowAddCameraModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors shadow-sm hover:shadow-md"
          >
            <Plus className="w-4 h-4" />
            <span>Add Camera</span>
          </button>
        </div>
      </div>

      {cameras.length === 0 ? (
        <div className="text-center py-8">
          <Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <div className="text-gray-500">No cameras found in this shop</div>
        </div>
      ) : (
        <div className="space-y-4">
          {cameras.map((camera) => (
            <CameraItem
              key={camera.id}
              camera={camera}
              operationInProgress={operationInProgress}
              onStartRecording={handleStartRecording}
              onStopRecording={handleStopRecording}
              onDeleteCamera={handleDeleteCamera}
            />
          ))}
        </div>
      )}

      <AddCameraModal
        shopId={shopId}
        isOpen={showAddCameraModal}
        onClose={() => setShowAddCameraModal(false)}
        onCameraAdded={handleCameraAdded}
      />
    </div>
  );
}
