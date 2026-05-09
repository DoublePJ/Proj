import { render, screen } from '@testing-library/react';
import RequireAuth from './RequireAuth';
import { useAuth } from '../contexts/AuthContext';

jest.mock('../contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

jest.mock('react-router-dom', () => ({
  Navigate: ({ to }) => <div data-testid="navigate" data-to={to} />,
}), { virtual: true });

describe('RequireAuth', () => {
  test('redirects to auth when unauthenticated', () => {
    useAuth.mockReturnValue({ isAuthenticated: false });

    render(<RequireAuth><div>secret</div></RequireAuth>);

    expect(screen.getByTestId('navigate')).toHaveAttribute('data-to', '/auth');
  });

  test('renders children when authenticated', () => {
    useAuth.mockReturnValue({ isAuthenticated: true });

    render(<RequireAuth><div>secret</div></RequireAuth>);

    expect(screen.getByText('secret')).toBeInTheDocument();
  });
});
