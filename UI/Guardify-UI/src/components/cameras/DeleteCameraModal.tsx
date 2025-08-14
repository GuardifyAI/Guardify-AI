import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

interface DeleteCameraModalProps {
  camera: {
    id: string;
    name: string;
  };
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export default function DeleteCameraModal({ camera, isOpen, onClose, onConfirm }: DeleteCameraModalProps) {
  if (!isOpen) return null;

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onConfirm();
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onKeyDown={handleKeyPress}
      tabIndex={-1}
    >
      <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-strong">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <h4 className="text-lg font-semibold text-gray-900">Delete Camera</h4>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="space-y-4">
          <div className="text-gray-600">
            <p>Are you sure you want to delete the camera <strong>"{camera.name}"</strong>?</p>
            <p className="mt-2 text-sm text-red-600">
              This action cannot be undone. All associated data will be permanently removed.
            </p>
          </div>
          
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={onConfirm}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 font-medium transition-colors"
            >
              Delete Camera
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
