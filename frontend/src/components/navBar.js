import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './navBar.css';
import conversationService from '../services/conversationService';
import { useAuth } from '../contexts/AuthContext';
import logo from '../assets/logo.svg';

function NavBar() {
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [indexFocus, setIndexFocus] = useState(null);
  const [isClosing, setIsClosing] = useState(false);
  const [historys, setHistorys] = useState([]);
  const { user } = useAuth();

  const closeMenu = () => {
    // play close animation then unmount
    setIsClosing(true);
    // duration should match CSS animation length (220ms) + small buffer
    setTimeout(() => {
      setIsMenuOpen(false);
      setIsClosing(false);
      setIndexFocus(null);
    }, 260);
  };

  const openMenu = () => {
    setIsMenuOpen(true);
    setIsClosing(false);
  };

  const handleMenuClick = () => {
    if (isMenuOpen) closeMenu();
    else openMenu();
  };

  // close on Escape
  useEffect(() => {
    if (!isMenuOpen) return;
    const onKey = (e) => {
      if (e.key === 'Escape') closeMenu();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isMenuOpen]);

  const handleFocusClick = (index) => {
    if (indexFocus === index) {
      setIndexFocus(null);
    } else {
      setIndexFocus(index);
    }
  };

  const handleClick = (to) => {
    navigate(to);
    closeMenu();
  }

  const handleKeyToggle = (index, e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleFocusClick(index);
    }
  };

  const handleClickHistory = async () => {
    try {
      // ดึงประวัติการสนทนา
      const history = await conversationService.getUserRooms(user.id);
      setHistorys(history);
    } catch (error) {
      console.error('Error getting chat history:', error);
      alert('ไม่สามารถโหลดประวัติการสนทนาได้');
    }
  };

  const handleDeleteHistory = async (roomId, e) => {
    e.stopPropagation();
    const confirmed = window.confirm('ยืนยันการลบประวัติการสนทนานี้?');
    if (!confirmed) return;
    try {
      await conversationService.deleteRoom(roomId);
      setHistorys((prev) => prev.filter((room) => room.id !== roomId));
    } catch (error) {
      console.error('Error deleting chat history:', error);
      alert('ไม่สามารถลบประวัติการสนทนาได้');
    }
  };

  const menuComponent = (
    <>
      <div className='menu-header'>
        <button className='close-btn' onClick={handleMenuClick} aria-label="Close menu" data-testid="menu-close-button">
          <span className="material-symbols-outlined" aria-hidden>
            arrow_back
          </span>
        </button>
        <span className="text-h1 brand" aria-hidden onClick={() => handleClick('/')}>
          <img src={logo} alt="Logo" className='menu-logo' />
          รายการ
        </span>
      </div>

      <nav className='menu-list' aria-label="Menu list">
        <button className="menu-item" onClick={() => handleClick('/')} data-testid="menu-new-chat-button">
          <span className='text-p'>แชตใหม่</span>
          <span className="material-symbols-outlined" aria-hidden>
            add_circle
          </span>
        </button>

        <button
          className="menu-item"
          onClick={() => handleClick('/library')}
          onKeyDown={(e) => handleKeyToggle(1, e)}
          aria-expanded={indexFocus === 1}
          aria-controls="library-panel"
          data-testid="menu-library-button"
        >
          <span className='text-p'>ห้องสมุดกฎหมาย</span>
          <span className="material-symbols-outlined" aria-hidden>
            {indexFocus === 1 ? 'arrow_circle_down' : 'arrow_circle_right'}
          </span>
        </button>
        {/* </div> */}

        <div className="menu-block-item">
          <button
            className="menu-item"
            onClick={() => { handleFocusClick(2); handleClickHistory(); }}
            onKeyDown={(e) => handleKeyToggle(2, e)}
            aria-expanded={indexFocus === 2}
            aria-controls="history-panel"
            aria-disabled="true"
            data-testid="menu-history-button"
          >
            <span className='text-p'>ประวัติการสนทนา</span>
            <span className="material-symbols-outlined" aria-hidden>
              {indexFocus === 2 ? 'arrow_circle_down' : 'arrow_circle_right'}
            </span>
          </button>

          {indexFocus === 2 && historys.length > 0 && (
            <div className='menu-subitem-list' id="history-panel">
              {historys.map((history) => (
                <div
                  key={history.id}
                  className='menu-subitem'
                  onClick={() => handleClick(`/chat/${history.id}`)}
                  data-testid={`history-item-${history.id}`}
                >
                  <span className="material-symbols-outlined rotate">
                    arrow_right
                  </span>
                  <span className="text-p">{history.title || 'ห้องสนทนาไม่มีชื่อ'}</span>
                  <button
                    type="button"
                    className="history-delete-btn"
                    onClick={(e) => handleDeleteHistory(history.id, e)}
                    aria-label="ลบประวัติการสนทนา"
                    data-testid={`history-delete-${history.id}`}
                  >
                    <span className="material-symbols-outlined" aria-hidden>
                      delete
                    </span>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </nav>
      <div style={{ padding: '15px', display: 'flex', justifyContent: 'center' }} >
        <button
          className="menu-item"
          onClick={() => handleClick('/account')}
          data-testid="menu-account-button"
        >
          <span className='text-p'>จัดการบัญชี</span>
        </button>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile navbar */}
      <div className='navbar-container'>
        <button className='menu-btn' onClick={handleMenuClick} aria-label="Open menu" data-testid="menu-open-button">
          <span className="material-symbols-outlined" aria-hidden>
            menu
          </span>
        </button>
        <span />
        <span />
      </div>

      {(isMenuOpen || isClosing) && (
        <aside className={`menu-panel ${isClosing ? 'closing' : ''}`} role="dialog" aria-modal="true" aria-label="Main menu" data-testid="menu-panel">
          {menuComponent}
        </aside>
      )}

      <nav className="desktop-navbar" aria-label="Primary">
        {menuComponent}
      </nav>
    </>
  );
}

export default NavBar;
