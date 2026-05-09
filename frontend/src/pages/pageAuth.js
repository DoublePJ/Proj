import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './pageAuth.css';
import logo from '../assets/logo.svg';

function PageAuth() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [authError, setAuthError] = useState(null);
    const [authMessage, setAuthMessage] = useState(null);
    const [isSignUp, setIsSignUp] = useState(true);
    const { signUp, signInWithGoogle, signIn, resetPassword, loading } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setAuthError(null);
        setAuthMessage(null);
        if (!email || !password) {
            setAuthError('โปรดกรอกอีเมลและรหัสผ่าน');
            return;
        }
        try {
            if (isSignUp) {
                console.log('Signing up with', email);
                await signUp({ email, password });
            } else {
                console.log('Signing in with', email);
                await signIn({ email, password });
            }
        } catch (err) {
            setAuthError(err.message || String(err));
        }
    };

    const handleGoogle = async () => {
        setAuthError(null);
        setAuthMessage(null);
        try {
            await signInWithGoogle();
        } catch (err) {
            setAuthError(err.message || String(err));
        }
    };

    const handleForgotPassword = async () => {
        setAuthError(null);
        setAuthMessage(null);

        if (!email) {
            setAuthError('โปรดกรอกอีเมลก่อนกดลืมรหัสผ่าน');
            return;
        }

        try {
            await resetPassword(email);
            setAuthMessage('ส่งลิงก์รีเซ็ตรหัสผ่านแล้ว กรุณาตรวจสอบอีเมล');
        } catch (err) {
            setAuthError(err.message || String(err));
        }
    };

    return (
        <div className="page-auth" data-testid="auth-page">
            <div className="auth-card">
                <div className="auth-inner">
                    <img src={logo} alt="logo" className="auth-logo" />
                    <span className="h1 auth-title">{isSignUp ? 'ลงทะเบียน' : 'ลงชื่อเข้าใช้'}</span>
                    <span className="p auth-sub">{isSignUp ? 'ลงทะเบียนสำหรับสร้างบัญชี' : 'ลงชื่อเพื่อเข้าใช้งานก่อนนะ !'}</span>

                    <button type="button" className="gsi-material-button google-btn" onClick={handleGoogle} disabled={loading} data-testid="auth-google-button">
                        <div className="gsi-material-button-state"></div>
                        <div className="gsi-material-button-content-wrapper">
                            <div className="gsi-material-button-icon">
                                <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" xmlnsXlink="http://www.w3.org/1999/xlink" style={{ display: 'block' }}>
                                    <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"></path>
                                    <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"></path>
                                    <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"></path>
                                    <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"></path>
                                    <path fill="none" d="M0 0h48v48H0z"></path>
                                </svg>
                            </div>
                            <span className="gsi-material-button-contents"><span className='small'>ดำเนินการต่อด้วย Google</span></span>
                            <span style={{ display: 'none' }}>ดำเนินการต่อด้วย Google</span>
                        </div>
                    </button>

                    <hr className="divider" />

                    <form className="auth-form" onSubmit={handleSubmit} data-testid="auth-form">
                        <label className="p input-label">อีเมล</label>
                        <div className="p input-pill">
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="p text-input"
                                placeholder="example@email.com"
                                data-testid="auth-email-input"
                            />
                        </div>

                        <label className="p input-label">รหัสผ่าน</label>
                        <div className="p input-pill password-pill">
                            <input
                                type={showPassword ? 'text' : 'password'}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="p text-input"
                                placeholder="•••••••"
                                data-testid="auth-password-input"
                            />
                            <button
                                type="button"
                                className="eye-btn material-symbols-outlined"
                                onClick={() => setShowPassword(!showPassword)}
                                aria-label="Toggle password visibility"
                                data-testid="auth-toggle-password"
                            >
                                {showPassword ? 'visibility' : 'visibility_off'}
                            </button>
                        </div>

                        {!isSignUp && (
                            <div className="form-row">
                                <span onClick={() => setIsSignUp(true)} className="small register-account" style={{ cursor: 'pointer' }} data-testid="auth-switch-to-signup">สร้างบัญชีใหม่</span>
                                <button type="button" className="small forgot-link-button" onClick={handleForgotPassword} data-testid="auth-forgot-password-button">ลืมรหัสผ่าน?</button>
                            </div>
                        )}
                        {isSignUp && (
                            <div className="form-row">
                                <span onClick={() => setIsSignUp(false)} className="small create-account" style={{ cursor: 'pointer' }} data-testid="auth-switch-to-signin">มีบัญชีอยู่แล้ว?</span>
                            </div>
                        )}

                        <button className="p submit-btn" type="submit" disabled={loading} data-testid="auth-submit-button">
                            {loading ? <span className='material-symbols-outlined'>hourglass_top</span> :
                                isSignUp ? 'ลงทะเบียน' : 'เข้าสู่ระบบ'}
                        </button>

                        {authError && <div className="auth-error" data-testid="auth-error">{authError}</div>}
                        {authMessage && <div className="auth-success" data-testid="auth-success">{authMessage}</div>}
                    </form>
                </div>
            </div>
        </div>
    );
}

export default PageAuth;
