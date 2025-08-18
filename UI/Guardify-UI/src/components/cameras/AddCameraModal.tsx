import React, { useState } from 'react';
import { Plus, X, Loader2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { cameraService } from '../../services/cameras';
import type { Camera } from '../../types/ui';

interface AddCameraModalProps {
  shopId: string;
  isOpen: boolean;
  onClose: () => void;
  onCameraAdded: (camera: Camera) => void;
}

export default function AddCameraModal({ shopId, isOpen, onClose, onCameraAdded }: AddCameraModalProps) {
  const [cameraName, setCameraName] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const { token } = useAuth();

  const handleAdd = async () => {
    if (!token || !cameraName.trim() || isAdding) return;

    setIsAdding(true);
    try {
      const response = await cameraService.createCamera(shopId, cameraName.trim(), token);
      
      if (response.result && !response.errorMessage) {
        // Create the new camera object
        const newCamera: Camera = {
          id: response.result.camera_id,
          shopId: response.result.shop_id,
          name: response.result.camera_name ?? '',
        };
        
        // Notify parent component
        onCameraAdded(newCamera);
        
        // Close modal and reset form
        handleClose();
      } else {
        alert(`Failed to add camera: ${response.errorMessage}`);
      }
    } catch (err) {
      alert('Failed to add camera');
      console.error('Error adding camera:', err);
    } finally {
      setIsAdding(false);
    }
  };

  const handleClose = () => {
    setCameraName('');
    onClose();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && cameraName.trim() && !isAdding) {
      handleAdd();
    } else if (e.key === 'Escape') {
      handleClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-strong">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-semibold text-gray-900">Add New Camera</h4>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={isAdding}
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="cameraName" className="block text-sm font-medium text-gray-700 mb-2">
              Camera Name
            </label>
            <input
              type="text"
              id="cameraName"
              value={cameraName}
              onChange={(e) => setCameraName(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Enter camera name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-colors"
              disabled={isAdding}
              autoFocus
            />
          </div>
          
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              onClick={handleClose}
              disabled={isAdding}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleAdd}
              disabled={isAdding || !cameraName.trim()}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAdding ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Adding...</span>
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  <span>Add Camera</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
