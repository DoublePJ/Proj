import { render, screen, fireEvent } from '@testing-library/react';
import ChatInput from './ChatInput';

describe('ChatInput', () => {
  test('submits non-empty message and clears input', () => {
    const onSendMessage = jest.fn();
    const { container } = render(<ChatInput onSendMessage={onSendMessage} isLoading={false} />);

    const input = screen.getByPlaceholderText('พิมพ์คำถามของคุณ...');
    fireEvent.change(input, { target: { value: '  สอบถามสิทธิ์ลางาน  ' } });
    fireEvent.submit(container.querySelector('form'));

    expect(onSendMessage).toHaveBeenCalledWith('  สอบถามสิทธิ์ลางาน  ');
    expect(input).toHaveValue('');
  });

  test('does not submit empty message or when loading', () => {
    const onSendMessage = jest.fn();
    const { rerender } = render(<ChatInput onSendMessage={onSendMessage} isLoading={false} />);

    const input = screen.getByPlaceholderText('พิมพ์คำถามของคุณ...');
    fireEvent.change(input, { target: { value: '   ' } });
    fireEvent.submit(input.closest('form'));
    expect(onSendMessage).not.toHaveBeenCalled();

    rerender(<ChatInput onSendMessage={onSendMessage} isLoading={true} />);
    expect(screen.getByPlaceholderText('พิมพ์คำถามของคุณ...')).toBeDisabled();
  });
});
