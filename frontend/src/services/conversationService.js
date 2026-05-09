import httpService from './httpService';

const conversationService = {
    // ===================== Chat Rooms =====================
    
    /**
     * สร้างห้องสนทนาใหม่
     * @param {Object} params - { user_id?, title? }
     * @returns {Promise} Room object
     */
    createRoom: async (params = {}) => {
        const { user_id = null, title = "การสนทนาใหม่" } = params;
        try {
            const response = await httpService.post('/api/conversations/rooms', {
                user_id,
                title
            });
            return response.data;
        } catch (error) {
            console.error('Error creating room:', error);
            throw error;
        }
    },

    /**
     * ดึงรายการห้องสนทนาทั้งหมด
     * @param {Object} params - { user_id?, include_archived? }
     * @returns {Promise} Array of room objects
     */
    getRooms: async (params = {}) => {
        const { user_id = null, include_archived = false } = params;
        try {
            const queryParams = new URLSearchParams();
            if (user_id) queryParams.append('user_id', user_id);
            queryParams.append('include_archived', include_archived);
            
            const response = await httpService.get(`/api/conversations/rooms?${queryParams}`);
            return response.data;
        } catch (error) {
            console.error('Error getting rooms:', error);
            throw error;
        }
    },

    /**
     * ดึงรายการห้องสนทนาของผู้ใช้คนหนึ่ง
     * @param {number|null} userId - ID ของผู้ใช้
     * @returns {Promise} Array of room objects
     */
    getUserRooms: async (userId) => {
        try {
            return await conversationService.getRooms({ 
                user_id: userId, 
                include_archived: false 
            });
        } catch (error) {
            console.error('Error getting user rooms:', error);
            throw error;
        }
    },

    /**
     * อัพเดทชื่อห้องสนทนา
     * @param {number} roomId - ID ของห้อง
     * @param {string} title - ชื่อใหม่
     * @returns {Promise} Updated room object
     */
    updateRoomTitle: async (roomId, title) => {
        try {
            return await conversationService.updateRoom(roomId, { title });
        } catch (error) {
            console.error('Error updating room title:', error);
            throw error;
        }
    },

    /**
     * ดึงข้อมูลห้องสนทนาตาม ID
     * @param {number} roomId
     * @returns {Promise} Room object
     */
    getRoom: async (roomId) => {
        try {
            const response = await httpService.get(`/api/conversations/rooms/${roomId}`);
            return response.data;
        } catch (error) {
            console.error('Error getting room:', error);
            throw error;
        }
    },

    /**
     * อัพเดทข้อมูลห้องสนทนา
     * @param {number} roomId
     * @param {Object} params - { title?, is_archive? }
     * @returns {Promise} Updated room object
     */
    updateRoom: async (roomId, params) => {
        try {
            const response = await httpService.put(`/api/conversations/rooms/${roomId}`, params);
            return response.data;
        } catch (error) {
            console.error('Error updating room:', error);
            throw error;
        }
    },

    /**
     * ลบห้องสนทนา
     * @param {number} roomId
     * @returns {Promise}
     */
    deleteRoom: async (roomId) => {
        try {
            const response = await httpService.delete(`/api/conversations/rooms/${roomId}`);
            return response.data;
        } catch (error) {
            console.error('Error deleting room:', error);
            throw error;
        }
    },

    /**
     * ลบห้องสนทนาทั้งหมดของผู้ใช้
     * @param {string} userId - ID ของผู้ใช้
     * @returns {Promise}
     */
    deleteUserRooms: async (userId) => {
        try {
            const response = await httpService.delete(`/api/conversations/rooms/by-user/${userId}`);
            return response.data;
        } catch (error) {
            console.error('Error deleting user rooms:', error);
            throw error;
        }
    },

    // ===================== Messages =====================

    /**
     * เพิ่มข้อความในห้องสนทนา
     * @param {number} roomId
     * @param {Object} params - { sender: 'user'|'bot', message: string, metadata?: Object }
     * @returns {Promise} Message object
     */
    addMessage: async (roomId, params) => {
        const { sender, message, metadata } = params;
        console.log('Adding message with metadata:', metadata);
        try {
            const response = await httpService.post(`/api/conversations/rooms/${roomId}/messages`, {
                sender,
                message,
                metadata: metadata || {}
            });
            return response.data;
        } catch (error) {
            console.error('Error adding message:', error);
            throw error;
        }
    },

    /**
     * ดึงข้อความทั้งหมดในห้องสนทนา
     * @param {number} roomId
     * @param {number} limit - จำนวนข้อความสูงสุด (default: 100)
     * @returns {Promise} Array of message objects
     */
    getMessages: async (roomId, limit = 100) => {
        try {
            const response = await httpService.get(`/api/conversations/rooms/${roomId}/messages?limit=${limit}`);
            return response.data;
        } catch (error) {
            console.error('Error getting messages:', error);
            throw error;
        }
    },

    /**
     * ดึงประวัติการสนทนาในรูปแบบที่พร้อมใช้กับ LLM
     * @param {number} roomId
     * @returns {Promise} Array of { role, content }
     */
    getHistory: async (roomId) => {
        try {
            const response = await httpService.get(`/api/conversations/rooms/${roomId}/history`);
            return response.data;
        } catch (error) {
            console.error('Error getting history:', error);
            throw error;
        }
    }
};

export default conversationService;
