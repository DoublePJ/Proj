import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import PageLanding from './pageLanding';
import conversationService from '../services/conversationService';
import { useAuth } from '../contexts/AuthContext';

jest.mock('../contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

jest.mock('../services/conversationService', () => ({
  __esModule: true,
  default: {
    createRoom: jest.fn(),
    addMessage: jest.fn(),
  },
}));

jest.mock('../components/ChatInput', () => function MockChatInput({ onSendMessage, isLoading }) {
  return (
    <button type="button" onClick={() => onSendMessage('สอบถามวันลาพักร้อน')} disabled={isLoading}>
      mock-chat-input
    </button>
  );
});

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}), { virtual: true });

describe('PageLanding', () => {
  beforeEach(() => {
    mockNavigate.mockReset();
    useAuth.mockReturnValue({ user: { id: 'user-1' } });
    conversationService.createRoom.mockResolvedValue({ id: 101 });
    conversationService.addMessage.mockResolvedValue({ id: 1 });
  });

  test('creates room, stores first message, and navigates to chat', async () => {
    render(<PageLanding />);

    fireEvent.click(screen.getByRole('button', { name: 'mock-chat-input' }));

    await waitFor(() => expect(conversationService.createRoom).toHaveBeenCalled());
    expect(conversationService.addMessage).toHaveBeenCalledWith(101, {
      sender: 'user',
      message: 'สอบถามวันลาพักร้อน'
    });
    expect(mockNavigate).toHaveBeenCalledWith('/chat/101', { state: { firstMessage: 'สอบถามวันลาพักร้อน' } });
  });
});
