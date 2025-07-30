import type { SidebarProps } from '../types';

export default function Sidebar({ shops, selectedShop, activeTab, setActiveTab, setSelectedShop }: SidebarProps) {
  return (
    <aside className="sidebar">
      <img src="/images/logo.png" alt="Guardify Logo" className="logo" />
      <div className="user-info">
        <strong>John Doe</strong>
        <p>Guardify Manager</p>
      </div>

      <nav>
        <ul className="sidebar-tabs">
          {selectedShop === null ? (
            <>
              <li>
                <button
                  className={`sidebar-tab${activeTab === 'dashboard' ? ' active' : ''}`}
                  onClick={() => {
                    setActiveTab('dashboard');
                    setSelectedShop(null);
                  }}
                >
                  All Shops Statistics
                </button>
              </li>
              {shops.map(shop => (
                <li key={shop.id}>
                  <button
                    className="sidebar-tab"
                    onClick={() => {
                      setActiveTab('statistics');
                      setSelectedShop(shop.id);
                    }}
                  >
                    {shop.name}
                  </button>
                </li>
              ))}
            </>
          ) : (
            <>
              <li>
                <button
                  className={`sidebar-tab${activeTab === 'statistics' ? ' active' : ''}`}
                  onClick={() => setActiveTab('statistics')}
                >
                  Statistics
                </button>
              </li>
              <li>
                <button
                  className={`sidebar-tab${activeTab === 'events' ? ' active' : ''}`}
                  onClick={() => setActiveTab('events')}
                >
                  Events
                </button>
              </li>
              <li>
                <button
                  className={`sidebar-tab${activeTab === 'cameras' ? ' active' : ''}`}
                  onClick={() => setActiveTab('cameras')}
                >
                  Cameras
                </button>
              </li>
              <li>
                <button
                  className="sidebar-tab"
                  onClick={() => {
                    setSelectedShop(null);
                    setActiveTab('dashboard');
                  }}
                >
                  Back to All Shops
                </button>
              </li>
            </>
          )}

          <li>
            <button className="sidebar-tab" onClick={() => setActiveTab('settings')}>Settings</button>
          </li>
          <li>
            <button className="sidebar-tab" onClick={() => setActiveTab('logout')}>Logout</button>
          </li>
        </ul>
      </nav>
    </aside>
  );
}
