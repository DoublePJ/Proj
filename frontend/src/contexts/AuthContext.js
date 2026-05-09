import React, { createContext, useContext, useState, useEffect } from 'react';
import { createClient } from "@supabase/supabase-js";
import userService from '../services/userService';

const supabase = createClient(process.env.REACT_APP_SUPABASE_URL, process.env.REACT_APP_SUPABASE_PUBLISHABLE_DEFAULT_KEY);

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null);
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let mounted = true;
        const init = async () => {
            setLoading(true);
            try {
                const { data } = await supabase.auth.getSession();
                if (data?.session) {
                    const s = data.session;
                    if (!mounted) return;
                    setSession(s);
                    setUser(s.user);
                    setIsAuthenticated(true);
                    localStorage.setItem('auth_user', JSON.stringify({ user: s.user, token: s.access_token }));
                }
            } catch (err) {
                console.warn('Error fetching session', err);
            } finally {
                if (mounted) setLoading(false);
            }
        };

        init();

        const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, s) => {
            if (s) {
                setSession(s);
                setUser(s.user);
                setIsAuthenticated(true);
                localStorage.setItem('auth_user', JSON.stringify({ user: s.user, token: s.access_token }));

                // สร้าง/อัพเดท user profile เมื่อ auth state เปลี่ยน (สำหรับ OAuth callback)
                if (event === 'SIGNED_IN' && s.user) {
                    try {
                        await userService.createOrUpdateUser({
                            user_id: s.user.id,
                            email: s.user.email,
                            display_name: s.user.user_metadata?.full_name || s.user.user_metadata?.name || s.user.user_metadata?.display_name || s.user.email?.split('@')[0],
                            avatar_url: s.user.user_metadata?.avatar_url || s.user.user_metadata?.picture
                        });
                    } catch (userError) {
                        console.error('Failed to create/update user profile on auth change:', userError);
                    }
                }
            } else {
                setSession(null);
                setUser(null);
                setIsAuthenticated(false);
                localStorage.removeItem('auth_user');
            }
        });

        return () => {
            mounted = false;
            subscription?.unsubscribe();
        };
    }, []);

    const signUp = async ({ email, password }) => {
        setLoading(true);
        try {
            const { data, error } = await supabase.auth.signUp({ email, password });
            if (error) throw error;

            // สร้าง user profile เฉพาะกรณีที่มี session แล้วเท่านั้น
            // (บางโปรเจกต์ Supabase ต้องยืนยันอีเมลก่อน จึงยังไม่มี token ณ จุดนี้)
            if (data?.session) {
                setSession(data.session);
                setUser(data.session.user);
                setIsAuthenticated(true);
                localStorage.setItem('auth_user', JSON.stringify({ user: data.session.user, token: data.session.access_token }));

                try {
                    await userService.createOrUpdateUser({
                        user_id: data.session.user.id,
                        email: data.session.user.email,
                        display_name: data.session.user.user_metadata?.display_name || data.session.user.email?.split('@')[0],
                        avatar_url: data.session.user.user_metadata?.avatar_url
                    });
                } catch (userError) {
                    console.error('Failed to create user profile:', userError);
                }
            }

            return data;
        } catch (err) {
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const signIn = async ({ email, password }) => {
        setLoading(true);
        try {
            const { data, error } = await supabase.auth.signInWithPassword({ email, password });
            if (error) throw error;
            console.log('Sign-in data:', data);
            if (data?.session) {
                setSession(data.session);
                setUser(data.session.user);
                setIsAuthenticated(true);
                localStorage.setItem('auth_user', JSON.stringify({ user: data.session.user, token: data.session.access_token }));

                // สร้าง/อัพเดท user profile (สำหรับกรณีที่ยังไม่มี)
                try {
                    await userService.createOrUpdateUser({
                        user_id: data.session.user.id,
                        email: data.session.user.email,
                        display_name: data.session.user.user_metadata?.display_name || data.session.user.email?.split('@')[0],
                        avatar_url: data.session.user.user_metadata?.avatar_url
                    });
                } catch (userError) {
                    console.error('Failed to create/update user profile:', userError);
                }
            }
            return data;
        } catch (err) {
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const signInWithGoogle = async () => {
        setLoading(true);
        try {
            const { data, error } = await supabase.auth.signInWithOAuth({ provider: 'google' })
            if (error) throw error;
            console.log('Google sign-in data:', data);
            if (data?.session) {
                setSession(data.session);
                setUser(data.session.user);
                setIsAuthenticated(true);
                localStorage.setItem('auth_user', JSON.stringify({ user: data.session.user, token: data.session.access_token }));
                
                // สร้าง/อัพเดท user profile จากข้อมูล Google
                try {
                    await userService.createOrUpdateUser({
                        user_id: data.session.user.id,
                        email: data.session.user.email,
                        display_name: data.session.user.user_metadata?.full_name || data.session.user.user_metadata?.name || data.session.user.email?.split('@')[0],
                        avatar_url: data.session.user.user_metadata?.avatar_url || data.session.user.user_metadata?.picture
                    });
                } catch (userError) {
                    console.error('Failed to create/update user profile:', userError);
                }
            }
            return data;
        } catch (err) {
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        try {
            await supabase.auth.signOut();
        } catch (err) {
            console.warn('Error signing out', err);
        }
        localStorage.removeItem('auth_user');
        setUser(null);
        setSession(null);
        setIsAuthenticated(false);
    };

    // Check user login via email/password or OAuth
    const isEmailPasswordUser = () => {
        if (!user?.app_metadata?.providers) return false;
        return user.app_metadata.providers.includes('email');
    };

    // Send password reset link to email
    const resetPassword = async (email) => {
        setLoading(true);
        try {
            const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
                redirectTo: `${window.location.origin}/reset-password`
            });
            if (error) throw error;
            return data;
        } catch (err) {
            throw err;
        } finally {
            setLoading(false);
        }
    };

    // Update password
    const updatePassword = async (newPassword) => {
        setLoading(true);
        try {
            const { data, error } = await supabase.auth.updateUser({
                password: newPassword
            });
            if (error) throw error;
            return data;
        } catch (err) {
            throw err;
        } finally {
            setLoading(false);
        }
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, user, session, loading, signUp, signIn, signInWithGoogle, logout, resetPassword, updatePassword, isEmailPasswordUser }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}

export default AuthContext;
