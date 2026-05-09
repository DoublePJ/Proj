import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import PageChat from './pageChat';
import conversationService from '../services/conversationService';
import { TextDecoder, TextEncoder } from 'util';

global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

const mockNavigate = jest.fn();
const mockSetOpenTrail = jest.fn();

jest.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
  useParams: () => ({ chat_id: '12' }),
  useLocation: () => ({ pathname: '/chat/12', state: { firstMessage: 'ถามสิทธิ์ลางาน' } }),
}), { virtual: true });

jest.mock('../services/conversationService', () => ({
  __esModule: true,
  default: {
    getRoom: jest.fn(),
    getMessages: jest.fn(),
    addMessage: jest.fn(),
  },
}));

jest.mock('../components/MessageList', () => function MockMessageList({ messages }) {
  return <div data-testid="message-list">{messages.map((message) => message.text).join('|')}</div>;
});

jest.mock('../components/ChatInput', () => function MockChatInput({ onSendMessage, isLoading }) {
  return (
    <button type="button" onClick={() => onSendMessage('ขอข้อมูลเรื่องค่าจ้าง')} disabled={isLoading}>
      mock-chat-input
    </button>
  );
});

jest.mock('../contexts/LibraryContext', () => ({
  useLibrary: () => ({
    fetchSectionsByActAndNumber: jest.fn(),
    setOpenTrail: mockSetOpenTrail,
  }),
}), { virtual: true });

function createStreamResponse(chunks) {
  let index = 0;

  return {
    ok: true,
    body: {
      getReader: () => ({
        read: async () => {
          if (index >= chunks.length) {
            return { done: true, value: undefined };
          }

          const value = Buffer.from(chunks[index], 'utf8');
          index += 1;
          return { done: false, value };
        },
      }),
    },
  };
}

describe('PageChat', () => {
  beforeEach(() => {
    mockNavigate.mockReset();
    mockSetOpenTrail.mockReset();
    conversationService.getRoom.mockResolvedValue({ id: 12, title: 'ห้องทดสอบ' });
    conversationService.getMessages.mockResolvedValue([
      { id: 1, sender: 'user', message: 'ข้อความเดิม', created_at: '2024-01-01T00:00:00.000Z' },
    ]);
    conversationService.addMessage.mockResolvedValue({ id: 99 });
    global.fetch = jest.fn().mockResolvedValue(
      createStreamResponse([
        '{"type":"metadata","data":{"acts":[[1,"พระราชบัญญัติแรงงาน"]],"sections":[{"section_number":"10"}]}}\n',
        '{"type":"content","data":"คำตอบจากสตรีม"}\n',
      ])
    );
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('loads chat history and streams the first landing message', async () => {
    render(<PageChat />);

    await waitFor(() => expect(conversationService.getRoom).toHaveBeenCalledWith('12'));
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());

    expect(screen.getByTestId('message-list')).toHaveTextContent('ข้อความเดิม');

    await waitFor(() => expect(conversationService.addMessage).toHaveBeenCalledWith('12', {
      sender: 'bot',
      message: 'คำตอบจากสตรีม',
      metadata: {
        acts: [[1, 'พระราชบัญญัติแรงงาน']],
        sections: [{ section_number: '10' }],
      },
    }));

    expect(mockNavigate).toHaveBeenCalledWith('/chat/12', { replace: true, state: {} });
  });

  test('saves a user message when sending from chat input', async () => {
    render(<PageChat />);

    await waitFor(() => expect(conversationService.getRoom).toHaveBeenCalled());
    fireEvent.click(screen.getByRole('button', { name: 'mock-chat-input' }));

    await waitFor(() => expect(conversationService.addMessage).toHaveBeenCalledWith('12', {
      sender: 'user',
      message: 'ขอข้อมูลเรื่องค่าจ้าง',
    }));
  });
});