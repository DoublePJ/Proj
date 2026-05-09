import { useState } from 'react';
import './ChatInput.css';

function ChatInput({ onSendMessage, isLoading }) {
    const [inputValue, setInputValue] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (!inputValue.trim() || isLoading) {
            return;
        }

        onSendMessage(inputValue);
        setInputValue('');
    };

    return (
        <form className="chat-input-form" onSubmit={handleSubmit} data-testid="chat-input-form">
            <div className="input-wrapper">
                <input
                    type="text"
                    className="chat-input text-p-without-color"
                    placeholder="พิมพ์คำถามของคุณ..."
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    disabled={isLoading}
                    data-testid="chat-input-field"
                />
                <button
                    type="submit"
                    className="send-button"
                    disabled={isLoading || !inputValue.trim()}
                    title="ส่งข้อความ (Enter)"
                    data-testid="chat-send-button"
                >
                    <span className="material-symbols-outlined">send</span>
                </button>
            </div>
            <div className="input-hint text-small-without-color">
                กดปุ่ม Enter เพื่อส่งข้อความ <br/>
                อ้างอิงข้อมูลจากสำนักงานคณะกรรมการกฤษฎีกา
            </div>
        </form>
    );
}

export default ChatInput;
