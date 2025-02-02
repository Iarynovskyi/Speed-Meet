const apiEndpoints = {
    url_auth: 'http://127.0.0.1:5005/',
    url_profile: 'http://127.0.0.1:5006/',
    url_search_room: 'http://127.0.0.1:5008/',

    auth: {
        register: '/register',
        login: '/login',
        protected: '/protected',
    },

    profile: {
        saveProfile: '/api/profile',
        saveHobbies: '/api/profile/hobbies',
        savePreferences: '/api/profile/preferences',
        getProfile: '/api/profile/<user>',
        getPreferences: '/api/profile/preferences/<user>',
        getCountries: '/api/countries',
        getHobbies: '/api/hobbies'
    },

    search_room: {
        findRoom: '/api/find_room',
        createVipRoom: '/api/vip_room',
        leaveRoom: '/api/leave_room'
    }

};
export default apiEndpoints;
