import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import NavBar from './navBar';
import conversationService from '../services/conversationService';
import { useAuth } from '../contexts/AuthContext';

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}), { virtual: true });

jest.mock('../contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

jest.mock('../services/conversationService', () => ({
  __esModule: true,
  default: {
    getUserRooms: jest.fn(),
    deleteRoom: jest.fn(),
  },
}));

describe('NavBar', () => {
  beforeEach(() => {
    mockNavigate.mockReset();
    useAuth.mockReturnValue({ user: { id: 'user-1' } });
    conversationService.getUserRooms.mockResolvedValue([
      { id: 11, title: 'ห้องสนทนาแรก' },
      { id: 22, title: 'ห้องสนทนาที่สอง' },
    ]);
    conversationService.deleteRoom.mockResolvedValue({ ok: true });
    window.confirm = jest.fn().mockReturnValue(true);
  });

  test('loads history, navigates to a room, and deletes history', async () => {
    render(<NavBar />);

    fireEvent.click(screen.getByRole('button', { name: 'Open menu' }));
    fireEvent.click(screen.getAllByRole('button', { name: 'ประวัติการสนทนา' })[0]);

    await waitFor(() => expect(conversationService.getUserRooms).toHaveBeenCalledWith('user-1'));
    const historyItems = await screen.findAllByText('ห้องสนทนาแรก');

    fireEvent.click(historyItems[0]);
    expect(mockNavigate).toHaveBeenCalledWith('/chat/11');

    fireEvent.click(screen.getAllByLabelText('ลบประวัติการสนทนา')[0]);

    await waitFor(() => expect(conversationService.deleteRoom).toHaveBeenCalledWith(11));
    await waitFor(() => expect(screen.queryByText('ห้องสนทนาแรก')).not.toBeInTheDocument());
  });

  test('navigates to account page from the menu', () => {
    render(<NavBar />);

    fireEvent.click(screen.getAllByRole('button', { name: 'จัดการบัญชี' })[0]);

    expect(mockNavigate).toHaveBeenCalledWith('/account');
  });
});