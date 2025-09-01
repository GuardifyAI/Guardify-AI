import { useState } from 'react';
import { Camera, Play, Square, Clock, Loader2, Trash2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { cameraService } from '../../services/cameras';
import DeleteCameraModal from './DeleteCameraModal';

interface CameraItemProps {
  camera: {
    id: string;
    shopId: string;
    name: string;
    isRecording: boolean;
    recordingStartedAt?: number;
  };
  operationInProgress: string | null;
  onStartRecording: (cameraName: string) => void;
  onStopRecording: (cameraName: string) => void;
  onDeleteCamera: (cameraId: string) => void;
}

export default function CameraItem({ 
  camera, 
  operationInProgress, 
  onStartRecording, 
  onStopRecording,
  onDeleteCamera 
}: CameraItemProps) {
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const { token } = useAuth();

  const formatRecordingTime = (startedAt: number) => {
    const elapsed = Math.floor((Date.now() - startedAt * 1000) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const handleDeleteConfirm = async () => {
    if (!token) return;

    try {
      const response = await cameraService.deleteCamera(camera.shopId, camera.id, token);
      
      if (response.result !== undefined && !response.errorMessage) {
        onDeleteCamera(camera.id);
        setShowDeleteModal(false);
      } else {
        alert(`Failed to delete camera: ${response.errorMessage}`);
      }
    } catch (err) {
      alert('Failed to delete camera');
      console.error('Error deleting camera:', err);
    }
  };

  const isOperationInProgress = operationInProgress === camera.name;

  return (
    <>
      <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
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
            onClick={() => onStartRecording(camera.name)}
            disabled={camera.isRecording || isOperationInProgress}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
              camera.isRecording || isOperationInProgress
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-green-500 text-white hover:bg-green-600 shadow-sm hover:shadow-md'
            }`}
          >
            {isOperationInProgress ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            <span>Start Record</span>
          </button>

          <button
            onClick={() => onStopRecording(camera.name)}
            disabled={!camera.isRecording || isOperationInProgress}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
              !camera.isRecording || isOperationInProgress
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-red-500 text-white hover:bg-red-600 shadow-sm hover:shadow-md'
            }`}
          >
            {isOperationInProgress ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Square className="w-4 h-4" />
            )}
            <span>Stop Record</span>
          </button>

          <button
            onClick={() => setShowDeleteModal(true)}
            disabled={camera.isRecording || isOperationInProgress}
            className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
              camera.isRecording || isOperationInProgress
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-gray-200 text-gray-700 hover:bg-red-100 hover:text-red-600 shadow-sm hover:shadow-md'
            }`}
            title={camera.isRecording ? 'Cannot delete camera while recording' : 'Delete camera'}
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <DeleteCameraModal
        camera={camera}
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDeleteConfirm}
      />
    </>
  );
}
