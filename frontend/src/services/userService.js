import httpService from './httpService';

const userService = {
    /**
     * สร้างหรืออัพเดท user profile
     * @param {Object} params - { user_id, email?, display_name?, avatar_url? }
     * @returns {Promise} User object
     */
    createOrUpdateUser: async (params) => {
        const { user_id, email = null, display_name = null, avatar_url = null } = params;
        try {
            const response = await httpService.post('/api/users/', {
                user_id,
                email,
                display_name,
                avatar_url
            });
            return response.data;
        } catch (error) {
            console.error('Error creating/updating user:', error);
            throw error;
        }
    },

    /**
     * ดึงข้อมูล user ตาม ID
     * @param {string} userId
     * @returns {Promise} User object
     */
    getUser: async (userId) => {
        try {
            const response = await httpService.get(`/api/users/${userId}`);
            return response.data;
        } catch (error) {
            console.error('Error getting user:', error);
            throw error;
        }
    },

    /**
     * อัพเดทข้อมูล user profile
     * @param {string} userId
     * @param {Object} params - { display_name?, avatar_url?, detail?, date_of_birth?, job_description?, start_work_date?, job_type_description? }
     * @returns {Promise} Updated user object
     */
    updateUser: async (userId, params) => {
        try {
            console.log('Updating user with params:', params);
            const response = await httpService.put(`/api/users/${userId}`, params);
            return response.data;
        } catch (error) {
            console.error('Error updating user:', error);
            throw error;
        }
    },

    /**
     * ลบ user profile
     * @param {string} userId
     * @returns {Promise}
     */
    deleteUser: async (userId) => {
        try {
            const response = await httpService.delete(`/api/users/${userId}`);
            return response.data;
        } catch (error) {
            console.error('Error deleting user:', error);
            throw error;
        }
    },

    /**
     * ดึงรายชื่อ job ทั้งหมด
     * @returns {Promise} Array of jobs
     */
    getJobs: async () => {
        try {
            const response = await httpService.get('/api/users/options/jobs');
            return response.data;
        } catch (error) {
            console.error('Error fetching jobs:', error);
            throw error;
        }
    },

    /**
     * ดึงรายชื่อ job_type ทั้งหมด
     * @returns {Promise} Array of job_types
     */
    getJobTypes: async () => {
        try {
            const response = await httpService.get('/api/users/options/job-types');
            return response.data;
        } catch (error) {
            console.error('Error fetching job types:', error);
            throw error;
        }
    }
};

export default userService;
