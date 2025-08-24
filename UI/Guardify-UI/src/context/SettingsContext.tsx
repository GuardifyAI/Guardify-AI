import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';

interface RecordingSettings {
  duration: number;
  detectionThreshold: number;
  analysisIterations: number;
}

interface SettingsContextType {
  recordingSettings: RecordingSettings;
  updateRecordingSettings: (settings: Partial<RecordingSettings>) => void;
  resetToDefaults: () => void;
}

const defaultSettings: RecordingSettings = {
  duration: 30,
  detectionThreshold: 0.8,
  analysisIterations: 1,
};

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export function useSettings() {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
}

interface SettingsProviderProps {
  children: ReactNode;
}

export function SettingsProvider({ children }: SettingsProviderProps) {
  const [recordingSettings, setRecordingSettings] = useState<RecordingSettings>(defaultSettings);

  // Load settings from localStorage on mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('guardify-recording-settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setRecordingSettings({ ...defaultSettings, ...parsed });
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
  }, []);

  // Save settings to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('guardify-recording-settings', JSON.stringify(recordingSettings));
  }, [recordingSettings]);

  const updateRecordingSettings = (settings: Partial<RecordingSettings>) => {
    setRecordingSettings(prev => ({ ...prev, ...settings }));
  };

  const resetToDefaults = () => {
    setRecordingSettings(defaultSettings);
  };

  const value: SettingsContextType = {
    recordingSettings,
    updateRecordingSettings,
    resetToDefaults,
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
}
