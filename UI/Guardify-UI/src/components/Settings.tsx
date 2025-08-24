import { useState } from 'react';
import { Settings as SettingsIcon, RotateCcw, Save, Camera, Brain, Clock } from 'lucide-react';
import { useSettings } from '../context/SettingsContext';

export default function Settings() {
  const { recordingSettings, updateRecordingSettings, resetToDefaults } = useSettings();
  const [localSettings, setLocalSettings] = useState(recordingSettings);
  const [hasChanges, setHasChanges] = useState(false);

  const handleChange = (key: keyof typeof localSettings, value: number) => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    setHasChanges(JSON.stringify(newSettings) !== JSON.stringify(recordingSettings));
  };

  const handleSave = () => {
    updateRecordingSettings(localSettings);
    setHasChanges(false);
  };

  const handleReset = () => {
    resetToDefaults();
    setLocalSettings(recordingSettings);
    setHasChanges(false);
  };

  const handleCancel = () => {
    setLocalSettings(recordingSettings);
    setHasChanges(false);
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-soft border border-gray-100">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
            <SettingsIcon className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Recording Settings</h2>
            <p className="text-sm text-gray-600">Configure default parameters for camera recordings</p>
          </div>
        </div>
        
        {hasChanges && (
          <div className="flex items-center space-x-2">
            <button
              onClick={handleCancel}
              className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors shadow-sm hover:shadow-md"
            >
              <Save className="w-4 h-4" />
              <span>Save Changes</span>
            </button>
          </div>
        )}
      </div>

      <div className="space-y-6">
        {/* Recording Duration */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center space-x-3 mb-3">
            <Clock className="w-5 h-5 text-gray-600" />
            <div>
              <h3 className="font-medium text-gray-900">Recording Duration</h3>
              <p className="text-sm text-gray-600">Default duration for video recordings (seconds)</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <input
              type="range"
              min="10"
              max="300"
              step="10"
              value={localSettings.duration}
              onChange={(e) => handleChange('duration', parseInt(e.target.value))}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider accent-primary-500"
            />
            <div className="flex items-center space-x-2">
              <input
                type="number"
                min="10"
                max="300"
                value={localSettings.duration}
                onChange={(e) => handleChange('duration', parseInt(e.target.value))}
                className="w-20 px-3 py-2 border border-gray-300 rounded-lg text-center focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
              <span className="text-sm text-gray-600">sec</span>
            </div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>10s</span>
            <span>5 minutes</span>
          </div>
        </div>

        {/* Detection Threshold */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center space-x-3 mb-3">
            <Camera className="w-5 h-5 text-gray-600" />
            <div>
              <h3 className="font-medium text-gray-900">Detection Threshold</h3>
              <p className="text-sm text-gray-600">Sensitivity for shoplifting detection (0.1 = very sensitive, 1.0 = very strict)</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.05"
              value={localSettings.detectionThreshold}
              onChange={(e) => handleChange('detectionThreshold', parseFloat(e.target.value))}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider accent-primary-500"
            />
            <div className="flex items-center space-x-2">
              <input
                type="number"
                min="0.1"
                max="1.0"
                step="0.05"
                value={localSettings.detectionThreshold}
                onChange={(e) => handleChange('detectionThreshold', parseFloat(e.target.value))}
                className="w-20 px-3 py-2 border border-gray-300 rounded-lg text-center focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>0.1 (Sensitive)</span>
            <span>1.0 (Strict)</span>
          </div>
        </div>

        {/* Analysis Iterations */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center space-x-3 mb-3">
            <Brain className="w-5 h-5 text-gray-600" />
            <div>
              <h3 className="font-medium text-gray-900">Analysis Iterations</h3>
              <p className="text-sm text-gray-600">Number of AI analysis passes (more iterations = higher accuracy, slower processing)</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <input
              type="range"
              min="1"
              max="3"
              step="1"
              value={localSettings.analysisIterations}
              onChange={(e) => handleChange('analysisIterations', parseInt(e.target.value))}
              className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider accent-primary-500"
            />
            <div className="flex items-center space-x-2">
              <input
                type="number"
                min="1"
                max="3"
                value={localSettings.analysisIterations}
                onChange={(e) => handleChange('analysisIterations', parseInt(e.target.value))}
                className="w-20 px-3 py-2 border border-gray-300 rounded-lg text-center focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
              <span className="text-sm text-gray-600">passes</span>
            </div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>1 (Fast)</span>
            <span>3 (Thorough)</span>
          </div>
        </div>

        {/* Current Settings Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Current Settings Summary</h4>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-blue-700 font-medium">Duration:</span>
              <span className="text-blue-800 ml-1">{recordingSettings.duration}s</span>
            </div>
            <div>
              <span className="text-blue-700 font-medium">Threshold:</span>
              <span className="text-blue-800 ml-1">{recordingSettings.detectionThreshold}</span>
            </div>
            <div>
              <span className="text-blue-700 font-medium">Iterations:</span>
              <span className="text-blue-800 ml-1">{recordingSettings.analysisIterations}</span>
            </div>
          </div>
        </div>

        {/* Reset to Defaults */}
        <div className="flex justify-center">
          <button
            onClick={handleReset}
            className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Reset to Defaults</span>
          </button>
        </div>
      </div>
    </div>
  );
}
