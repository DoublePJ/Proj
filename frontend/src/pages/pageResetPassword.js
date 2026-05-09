import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import logo from '../assets/logo.svg';
import "./pageAuth.css";
import "./pageResetPassword.css";

function PageResetPassword() {
    const navigate = useNavigate();
    const location = useLocation();
    const { updatePassword, session } = useAuth();
    
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');
    const [isValid, setIsValid] = useState(false);

    useEffect(() => {
        // รองรับทั้ง query string (?...) และ hash fragment (#...) จาก Supabase recovery link
        const queryParams = new URLSearchParams(location.search);
        const hashParams = new URLSearchParams(location.hash.startsWith('#') ? location.hash.slice(1) : location.hash);

        const accessToken = queryParams.get('access_token') || hashParams.get('access_token');
        const recoveryType = queryParams.get('type') || hashParams.get('type');
        const code = queryParams.get('code') || hashParams.get('code');
        const tokenHash = queryParams.get('token_hash') || hashParams.get('token_hash');
        const errorDescription = queryParams.get('error_description') || hashParams.get('error_description');

        if (errorDescription) {
            setIsValid(false);
            setError(decodeURIComponent(errorDescription));
            return;
        }

        // Supabase recovery link อาจมาได้หลายรูปแบบขึ้นกับ flow (implicit/pkce)
        const hasRecoverySignal = Boolean(
            accessToken || code || tokenHash || recoveryType === 'recovery' || session
        );

        if (hasRecoverySignal) {
            setIsValid(true);
            setError('');
        } else {
            setIsValid(false);
            setError('ลิงค์รีเซ็ตรหัสผ่านไม่ถูกต้องหรือหมดอายุแล้ว');
        }
    }, [location.search, location.hash, session]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setMessage('');

        if (!newPassword || !confirmPassword) {
            setError('โปรดกรอกรหัสผ่านในทั้งสองช่อง');
            return;
        }

        if (newPassword !== confirmPassword) {
            setError('รหัสผ่านไม่ตรงกัน');
            return;
        }

        if (newPassword.length < 6) {
            setError('รหัสผ่านต้องยาวอย่างน้อย 6 ตัวอักษร');
            return;
        }

        setLoading(true);

        try {
            await updatePassword(newPassword);
            setMessage('รหัสผ่านของคุณได้รับการอัปเดตเรียบร้อยแล้ว');
            setTimeout(() => {
                navigate('/account');
            }, 2000);
        } catch (error) {
            setError('ไม่สามารถอัปเดตรหัสผ่านได้: ' + error.message);
            console.error('Update password error:', error);
        } finally {
            setLoading(false);
        }
    };

    if (!isValid) {
        return (
            <div className="page-reset-password">
                <div className="auth-card reset-auth-card">
                    <div className="auth-inner">
                        <img src={logo} alt="logo" className="auth-logo" />
                        <span className="h1 auth-title">เปลี่ยนรหัสผ่าน</span>
                        <span className="p auth-sub">ลิงก์นี้ไม่ถูกต้องหรือหมดอายุแล้ว</span>
                        <div className="auth-error" data-testid="reset-password-invalid-link">
                            {error}
                        </div>
                        <button
                            type="button"
                            onClick={() => navigate('/')}
                            className="p submit-btn reset-submit-btn"
                        >
                            กลับไปหน้าเข้าสู่ระบบ
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="page-reset-password">
            <div className="auth-card reset-auth-card">
                <div className="auth-inner">
                    <img src={logo} alt="logo" className="auth-logo" />
                    <span className="h1 auth-title">เปลี่ยนรหัสผ่าน</span>
                    <span className="p auth-sub">ตั้งรหัสผ่านใหม่เพื่อเข้าใช้งานบัญชีของคุณ</span>

                    <form onSubmit={handleSubmit} className="auth-form" data-testid="reset-password-form">
                        <label htmlFor="new-password" className="p input-label">รหัสผ่านใหม่</label>
                        <div className="p input-pill">
                            <input
                                id="new-password"
                                type="password"
                                className="p text-input"
                                placeholder="กรุณาป้อนรหัสผ่านใหม่"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                disabled={loading}
                                data-testid="reset-password-new-input"
                            />
                        </div>

                        <label htmlFor="confirm-password" className="p input-label">ยืนยันรหัสผ่าน</label>
                        <div className="p input-pill">
                            <input
                                id="confirm-password"
                                type="password"
                                className="p text-input"
                                placeholder="กรุณาป้อนรหัสผ่านอีกครั้ง"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                disabled={loading}
                                data-testid="reset-password-confirm-input"
                            />
                        </div>

                        {error && (
                            <div className="auth-error" data-testid="reset-password-error">
                                {error}
                            </div>
                        )}

                        {message && (
                            <div className="auth-success" data-testid="reset-password-success">
                                {message}
                            </div>
                        )}

                        <button
                            type="submit"
                            className="p submit-btn reset-submit-btn"
                            disabled={loading}
                            data-testid="reset-password-submit"
                        >
                            {loading ? 'กำลังอัปเดต...' : 'อัปเดตรหัสผ่าน'}
                        </button>

                        <button
                            type="button"
                            onClick={() => navigate('/')}
                            className="p reset-secondary-btn"
                            disabled={loading}
                            data-testid="reset-password-back-to-login"
                        >
                            กลับไปหน้าเข้าสู่ระบบ
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default PageResetPassword;
