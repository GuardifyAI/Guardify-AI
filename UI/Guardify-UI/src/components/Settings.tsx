import { useState } from 'react';
import { Settings as SettingsIcon, RotateCcw, Save, Camera, Brain, Clock } from 'lucide-react';
import { useSettings } from '../context/SettingsContext';

// Settings configuration
const SETTINGS_CONFIG = {
  duration: {
    min: 10,
    max: 300,
    step: 10,
    unit: 'sec',
    icon: Clock,
    title: 'Recording Duration',
    description: 'Default duration for video recordings (seconds)',
    rangeLabels: ['10s', '5 minutes']
  },
  detectionThreshold: {
    min: 0.1,
    max: 1.0,
    step: 0.05,
    unit: '',
    icon: Camera,
    title: 'Detection Threshold',
    description: 'Sensitivity for shoplifting detection (0.1 = very sensitive, 1.0 = very strict)',
    rangeLabels: ['0.1 (Sensitive)', '1.0 (Strict)']
  },
  analysisIterations: {
    min: 1,
    max: 3,
    step: 1,
    unit: 'passes',
    icon: Brain,
    title: 'Analysis Iterations',
    description: 'Number of AI analysis passes (more iterations = higher accuracy, slower processing)',
    rangeLabels: ['1 (Fast)', '3 (Thorough)']
  }
} as const;

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

  // Reusable setting item component
  const SettingItem = ({ 
    settingKey, 
    config 
  }: { 
    settingKey: keyof typeof SETTINGS_CONFIG; 
    config: typeof SETTINGS_CONFIG[keyof typeof SETTINGS_CONFIG] 
  }) => {
    const IconComponent = config.icon;
    const value = localSettings[settingKey];
    
    return (
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center space-x-3 mb-3">
          <IconComponent className="w-5 h-5 text-gray-600" />
          <div>
            <h3 className="font-medium text-gray-900">{config.title}</h3>
            <p className="text-sm text-gray-600">{config.description}</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <input
            type="range"
            min={config.min}
            max={config.max}
            step={config.step}
            value={value}
            onChange={(e) => handleChange(settingKey, parseFloat(e.target.value))}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider accent-primary-500"
          />
          <div className="flex items-center space-x-2">
            <input
              type="number"
              min={config.min}
              max={config.max}
              step={config.step}
              value={value}
              onChange={(e) => handleChange(settingKey, parseFloat(e.target.value))}
              className="w-20 px-3 py-2 border border-gray-300 rounded-lg text-center focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            {config.unit && <span className="text-sm text-gray-600">{config.unit}</span>}
          </div>
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{config.rangeLabels[0]}</span>
          <span>{config.rangeLabels[1]}</span>
        </div>
      </div>
    );
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
        {/* Dynamically render all settings */}
        {Object.entries(SETTINGS_CONFIG).map(([key, config]) => (
          <SettingItem 
            key={key}
            settingKey={key as keyof typeof SETTINGS_CONFIG}
            config={config}
          />
        ))}

        {/* Current Settings Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Current Settings Summary</h4>
          <div className="grid grid-cols-3 gap-4 text-sm">
            {Object.entries(SETTINGS_CONFIG).map(([key, config]) => (
              <div key={key}>
                <span className="text-blue-700 font-medium">{config.title.split(' ')[0]}:</span>
                <span className="text-blue-800 ml-1">
                  {recordingSettings[key as keyof typeof recordingSettings]}
                  {config.unit && config.unit}
                </span>
              </div>
            ))}
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
