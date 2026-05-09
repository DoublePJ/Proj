import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import PageAccount from './pageAccount';
import { useAuth } from '../contexts/AuthContext';
import userService from '../services/userService';

jest.mock('../contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

jest.mock('../services/userService', () => ({
  __esModule: true,
  default: {
    getJobs: jest.fn(),
    getJobTypes: jest.fn(),
    getUser: jest.fn(),
    updateUser: jest.fn(),
  },
}));

describe('PageAccount', () => {
  beforeEach(() => {
    useAuth.mockReturnValue({
      user: { id: 'user-1', email: 'user@example.com' },
      logout: jest.fn(),
    });
    userService.getJobs.mockResolvedValue([{ id: 1, description: 'พนักงาน' }]);
    userService.getJobTypes.mockResolvedValue([{ id: 1, description: 'เต็มเวลา' }]);
    userService.getUser.mockResolvedValue({
      date_of_birth: '1990-01-01',
      job_description: 'พนักงาน',
      start_work_date: '2020-01-01',
      job_type_description: 'เต็มเวลา',
    });
    userService.updateUser.mockResolvedValue({ id: 'user-1' });
  });

  test('loads user profile and submits updated data', async () => {
    render(<PageAccount />);

    await waitFor(() => expect(userService.getUser).toHaveBeenCalledWith('user-1'));
    await waitFor(() => expect(screen.getByRole('button', { name: /บันทึกการเปลี่ยนแปลง/i })).not.toBeDisabled());
    expect(screen.getByDisplayValue('user@example.com')).toBeDisabled();

    fireEvent.click(screen.getByRole('button', { name: 'บันทึกการเปลี่ยนแปลง' }));

    await waitFor(() => expect(userService.updateUser).toHaveBeenCalled());
    expect(userService.updateUser).toHaveBeenCalledWith('user-1', {
      date_of_birth: '1990-01-01',
      job_description: 'พนักงาน',
      start_work_date: '2020-01-01',
      job_type_description: 'เต็มเวลา',
    });
  });

  test('calls logout when clicking logout button', async () => {
    const auth = {
      user: { id: 'user-1', email: 'user@example.com' },
      logout: jest.fn(),
    };
    useAuth.mockReturnValue(auth);
    userService.getJobs.mockResolvedValue([{ id: 1, description: 'พนักงาน' }]);
    userService.getJobTypes.mockResolvedValue([{ id: 1, description: 'เต็มเวลา' }]);
    userService.getUser.mockResolvedValue({});

    render(<PageAccount />);
    await waitFor(() => expect(userService.getUser).toHaveBeenCalledWith('user-1'));
    fireEvent.click(screen.getByRole('button', { name: 'ออกจากระบบ' }));

    expect(auth.logout).toHaveBeenCalled();
  });
});
