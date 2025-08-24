import { 
  Shield, 
  BarChart3, 
  Store, 
  AlertTriangle, 
  Camera, 
  ArrowLeft, 
  Settings, 
  LogOut,
  User,
  MapPin
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import type { SidebarProps } from '../types/ui';

export default function Sidebar({ shops, selectedShop, activeTab, setActiveTab, setSelectedShop }: SidebarProps) {
  const { logout, user } = useAuth();
  
  const handleLogout = () => {
    logout();
  };

  return (
    <aside className="fixed left-0 top-0 h-full w-72 bg-gray-900 text-white shadow-strong z-50 flex flex-col transform transition-transform duration-300 ease-in-out lg:translate-x-0">
      {/* Logo and Brand */}
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-500 rounded-xl flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold">Guardify AI</h1>
            <p className="text-xs text-gray-400">Surveillance Management</p>
          </div>
        </div>
      </div>

      {/* User Profile */}
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gray-600 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-gray-300" />
          </div>
          <div>
            <p className="font-medium text-white">{user ? `${user.firstName} ${user.lastName}` : 'User'}</p>
            <p className="text-sm text-gray-400">Security Manager</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {selectedShop === null ? (
          <>
            {/* Main Dashboard */}
            <button
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                activeTab === 'dashboard' 
                  ? 'bg-primary-500 text-white shadow-medium' 
                  : 'text-blue-400 font-bold bg-blue-50 hover:bg-blue-100 hover:text-blue-700'
              }`}
              onClick={() => {
                setActiveTab('dashboard');
                setSelectedShop(null);
              }}
            >
              <BarChart3 className={`w-5 h-5 ${activeTab !== 'dashboard' ? 'text-blue-500' : ''}`} />
              <span className="font-medium">
                {activeTab === 'dashboard' ? 'Dashboard Overview' : '← Back to Dashboard'}
              </span>
            </button>

            {/* Individual Shops */}
            <div className="pt-4">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3 px-4">
                Shop Locations
              </p>
              {shops.map(shop => (
                <button
                  key={shop.id}
                  className="w-full flex items-center justify-between px-4 py-3 rounded-xl text-left transition-all duration-200 text-gray-300 hover:bg-gray-800 hover:text-white group"
                  onClick={() => {
                    console.log('Sidebar: Shop clicked:', shop.id, shop.name);
                    setActiveTab('statistics');
                    setSelectedShop(shop.id);
                  }}
                >
                  <div className="flex items-center space-x-3">
                    <Store className="w-5 h-5" />
                    <span className="font-medium">{shop.name}</span>
                  </div>
                  <div className="flex items-center">
                    <MapPin className="w-4 h-4 opacity-50 group-hover:opacity-100" />
                  </div>
                </button>
              ))}
            </div>
          </>
        ) : (
          <>
            {/* Shop-specific navigation */}
            <div className="mb-4">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3 px-4">
                {shops.find(s => s.id === selectedShop)?.name} Management
              </p>
            </div>

            <button
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                activeTab === 'statistics' 
                  ? 'bg-primary-500 text-white shadow-medium' 
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
              onClick={() => setActiveTab('statistics')}
            >
              <BarChart3 className="w-5 h-5" />
              <span className="font-medium">Statistics</span>
            </button>

            <button
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                activeTab === 'events' 
                  ? 'bg-primary-500 text-white shadow-medium' 
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
              onClick={() => setActiveTab('events')}
            >
              <AlertTriangle className="w-5 h-5" />
              <span className="font-medium">Security Events</span>
            </button>

            <button
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
                activeTab === 'cameras' 
                  ? 'bg-primary-500 text-white shadow-medium' 
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
              onClick={() => setActiveTab('cameras')}
            >
              <Camera className="w-5 h-5" />
              <span className="font-medium">Live Cameras</span>
            </button>

            {/* Back to Dashboard */}
            <div className="pt-4 border-t border-gray-700 mt-4">
              <button
                className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 text-gray-300 hover:bg-gray-800 hover:text-white"
                onClick={() => {
                  setSelectedShop(null);
                  setActiveTab('dashboard');
                }}
              >
                <ArrowLeft className="w-5 h-5" />
                <span className="font-medium">Back to Overview</span>
              </button>
            </div>
          </>
        )}
      </nav>

      {/* Bottom Actions */}
      <div className="p-4 border-t border-gray-700 space-y-2">
        <button 
          className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 ${
            activeTab === 'settings' 
              ? 'bg-primary-500 text-white shadow-medium' 
              : 'text-gray-300 hover:bg-gray-800 hover:text-white'
          }`}
          onClick={() => {
            setSelectedShop(null);
            setActiveTab('settings');
          }}
        >
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </button>
        
        <button 
          onClick={handleLogout}
          className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 text-gray-300 hover:bg-red-600 hover:text-white"
        >
          <LogOut className="w-5 h-5" />
          <span className="font-medium">Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
