import axios from 'axios';

const httpService = axios.create({
    baseURL: process.env.REACT_APP_BASE_API_URL || 'http://localhost:10000',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// เพิ่ม interceptor เพื่อใส่ Authorization header
httpService.interceptors.request.use(
    (config) => {
        // ดึง accessToken จาก localStorage ที่ถูกเก็บไว้จาก AuthContext
        const authData = localStorage.getItem('auth_user');
        if (authData) {
            try {
                const { token } = JSON.parse(authData);
                if (token) {
                    config.headers.Authorization = `Bearer ${token}`;
                }
            } catch (error) {
                console.error('Error parsing auth data from localStorage:', error);
            }
        }
        // console.log('HTTP Request:', config.method.toUpperCase(), config.url, 'Headers:', config.headers);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default httpService;