import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import conversationService from '../services/conversationService';
import MessageList from '../components/MessageList';
import ChatInput from '../components/ChatInput';
import './pageChat.css';

function PageChat() {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [roomInfo, setRoomInfo] = useState(null);
    const navigate = useNavigate();
    const { chat_id } = useParams();
    const location = useLocation();
    const hasProcessedFirstMessage = useRef(false);
    const hasLoadedHistory = useRef(false);
    const messagesRef = useRef(messages);

    // Update ref ทุกครั้งที่ messages เปลี่ยน
    useEffect(() => {
        messagesRef.current = messages;
    }, [messages]);

    // รีเซ็ตสถานะเมื่อเปลี่ยนห้อง
    useEffect(() => {
        setMessages([]);
        hasLoadedHistory.current = false;
        hasProcessedFirstMessage.current = false;
    }, [chat_id]);

    const handleStreamResponse = useCallback(async (userMessageText) => {
        // สร้าง assistant message ว่างๆ ไว้ก่อน
        const assistantMessageId = Date.now();
        const assistantMessage = {
            id: assistantMessageId,
            type: 'assistant',
            text: '',
            timestamp: new Date(),
            metadata: null,
            isLoading: true
        };
        setMessages(prev => [...prev, assistantMessage]);
        setIsLoading(true);

        try {
            // เรียก streaming API
            const baseURL = process.env.REACT_APP_BASE_API_URL || 'http://localhost:8000';
            const response = await fetch(`${baseURL}/llm/chat_stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: userMessageText,
                    history: messagesRef.current
                        .filter(m => m.type !== 'error' && !m.isLoading)
                        .map(msg => ({ content: msg.text, role: msg.type }))
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let metadata = null;
            let assistantText = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line !== '') {
                        try {
                            const parsed = JSON.parse(line);

                            if (parsed.type === 'metadata') {
                                metadata = parsed.data || {};
                                setMessages(prev => prev.map(msg =>
                                    msg.id === assistantMessageId
                                        ? { ...msg, metadata: parsed.data }
                                        : msg
                                ));
                            } else if (parsed.type === 'content') {
                                assistantText = assistantText + (parsed.data || '');
                                setMessages(prev => prev.map(msg =>
                                    msg.id === assistantMessageId
                                        ? { ...msg, text: (msg.text + parsed.data) }
                                        : msg
                                ));
                            }
                        } catch (e) {
                            console.log('Non-JSON data:', line);
                        }
                    }
                }
            }

            // บันทึกข้อความของ bot ลงฐานข้อมูล
            if (chat_id && assistantText) {
                try {
                    console.log('Saving bot message with metadata:', metadata);
                    await conversationService.addMessage(chat_id, {
                        sender: 'bot',
                        message: assistantText,
                        metadata: metadata || {}
                    });
                } catch (error) {
                    console.error('Failed to save bot message:', error);
                }
            }

        } catch (error) {
            console.error('Error sending message:', error);
            setMessages(prev => prev.map(msg =>
                msg.id === assistantMessageId
                    ? { ...msg, type: 'error', text: 'เกิดข้อผิดพลาดในการส่งข้อความ กรุณาลองใหม่อีกครั้ง' }
                    : msg
            ));
        } finally {
            setIsLoading(false);
            setMessages(prev => prev.map(msg =>
                msg.id === assistantMessageId
                    ? { ...msg, isLoading: false }
                    : msg
            ));
        }
    }, [chat_id]);

    // โหลดประวัติการสนทนาเมื่อเข้าหน้า
    useEffect(() => {
        const loadChatHistory = async () => {
            if (!chat_id) {
                navigate('/');
                return;
            }

            if (hasLoadedHistory.current) {
                return;
            }

            try {
                // ดึงข้อมูลห้อง
                const room = await conversationService.getRoom(chat_id);
                setRoomInfo(room);

                // ดึงประวัติข้อความ
                const history = await conversationService.getMessages(chat_id);

                // แปลง format จาก API เป็น format ที่ใช้ใน component
                const formattedMessages = history.map((msg, idx) => ({
                    id: msg.id || idx,
                    type: msg.sender === 'user' ? 'user' : 'assistant',
                    text: msg.message,
                    timestamp: new Date(msg.created_at),
                    metadata: msg.sender === 'user' ? null : msg.metadata || null
                }));
                console.log('Loaded chat history:', formattedMessages);

                setMessages(prev => (prev.length > 0 ? prev : formattedMessages));
                hasLoadedHistory.current = true;

                // ถ้ามี firstMessage จาก landing page ให้เริ่ม stream
                const firstMessage = location.state?.firstMessage;
                if (firstMessage && !hasProcessedFirstMessage.current) {
                    hasProcessedFirstMessage.current = true;
                    handleStreamResponse(firstMessage);
                    // เคลียร์ state เพื่อป้องกันเรียกซ้ำจาก StrictMode
                    navigate(location.pathname, { replace: true, state: {} });
                }
            } catch (error) {
                console.error('Error loading chat history:', error);
                alert('ไม่สามารถโหลดประวัติการสนทนาได้');
                navigate('/');
            }
        };

        loadChatHistory();
    }, [chat_id, navigate, handleStreamResponse, location.pathname, location.state]);

    const handleSendMessage = async (userMessageText) => {
        if (!userMessageText.trim() || isLoading) {
            return;
        }

        // เพิ่ม user message ลงใน chat
        const userMessage = {
            id: Date.now(),
            type: 'user',
            text: userMessageText,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);

        // บันทึกข้อความของ user ลงฐานข้อมูล
        if (chat_id) {
            try {
                await conversationService.addMessage(chat_id, {
                    sender: 'user',
                    message: userMessageText
                });
            } catch (error) {
                console.error('Failed to save user message:', error);
            }
        }

        // เริ่ม stream response
        await handleStreamResponse(userMessageText);
    };

    return (
        <div className="chat-container" data-testid="chat-page">
            <div className="chat-header" data-testid="chat-header">
                <span className="text-h2" data-testid="chat-room-title">{roomInfo?.title || 'กำลังโหลด...'}</span>
                <span className="p chat-subtitle">ถามคำถามเกี่ยวกับกฎหมายแรงงานไทย</span>
            </div>

            <MessageList messages={messages} />

            <ChatInput
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
            />
        </div>
    );
}

export default PageChat;
