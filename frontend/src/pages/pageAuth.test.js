import { render, screen, fireEvent } from '@testing-library/react';
import PageAuth from './pageAuth';
import { useAuth } from '../contexts/AuthContext';

jest.mock('../contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

describe('PageAuth', () => {
  const makeAuth = (overrides = {}) => ({
    signUp: jest.fn().mockResolvedValue({}),
    signIn: jest.fn().mockResolvedValue({}),
    signInWithGoogle: jest.fn().mockResolvedValue({}),
    loading: false,
    ...overrides,
  });

  test('shows validation error when email or password is missing', () => {
    useAuth.mockReturnValue(makeAuth());
    render(<PageAuth />);

    fireEvent.click(screen.getByRole('button', { name: 'ลงทะเบียน' }));

    expect(screen.getByText('โปรดกรอกอีเมลและรหัสผ่าน')).toBeInTheDocument();
  });

  test('calls signUp with form values by default', async () => {
    const auth = makeAuth();
    useAuth.mockReturnValue(auth);
    render(<PageAuth />);

    fireEvent.change(screen.getByPlaceholderText('example@email.com'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('•••••••'), { target: { value: 'secret123' } });
    fireEvent.click(screen.getByRole('button', { name: 'ลงทะเบียน' }));

    expect(auth.signUp).toHaveBeenCalledWith({ email: 'test@example.com', password: 'secret123' });
  });

  test('switches to sign in mode and calls signIn', () => {
    const auth = makeAuth();
    useAuth.mockReturnValue(auth);
    render(<PageAuth />);

    fireEvent.click(screen.getByText('มีบัญชีอยู่แล้ว?'));
    fireEvent.change(screen.getByPlaceholderText('example@email.com'), { target: { value: 'user@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('•••••••'), { target: { value: 'pass1234' } });
    fireEvent.click(screen.getByRole('button', { name: 'เข้าสู่ระบบ' }));

    expect(auth.signIn).toHaveBeenCalledWith({ email: 'user@example.com', password: 'pass1234' });
  });

  test('calls google sign in handler', () => {
    const auth = makeAuth();
    useAuth.mockReturnValue(auth);
    render(<PageAuth />);

    fireEvent.click(screen.getByRole('button', { name: /ดำเนินการต่อด้วย Google/i }));

    expect(auth.signInWithGoogle).toHaveBeenCalled();
  });
});
