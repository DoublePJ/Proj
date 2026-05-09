export const getFetchFunction = (type) => {
    switch (type) {
        case "tags": return fetchTags;
        case "acts": return fetchActs;
        case "books": return fetchBooks;
        case "groups": return fetchGroups;
        case "super_sections": return fetchSuperSections;
        case "sections": return fetchSections;
        default: return null;
    }
}
export const fetchTags = async () => {
    return httpService.get('/api/libraries/tags')
        .then(response => {
            console.log('Fetched tags:', response.data);
            return response.data;
        })
        .catch(error => {
            console.error('Error fetching tags:', error);
            return [];
        });
}
export const fetchActs = async () => {
    return httpService.get('/api/libraries/acts')
        .then(response => {
            console.log('Fetched acts:', response.data);
            return response.data;
        })
        .catch(error => {
            console.error('Error fetching acts:', error);
            return [];
        });
}
export const fetchBooks = async (act_id) => {
    return httpService.get(`/api/libraries/acts/${act_id}/books`)
        .then(response => {
            console.log('Fetched act books:', response.data);
            return response.data;
        })
        .catch(error => {
            console.error('Error fetching act books:', error);
            return [];
        });
}
export const fetchGroups = async (book_id) => {
    return httpService.get(`/api/libraries/books/${book_id}/groups`)
        .then(response => {
            console.log('Fetched book groups:', response.data);
            return response.data;
        })
        .catch(error => {
            console.error('Error fetching book groups:', error);
            return [];
        });
}
export const fetchSuperSections = async (group_id) => {
    return httpService.get(`/api/libraries/groups/${group_id}/super_sections`)
        .then(response => {
            console.log('Fetched group super sections:', response.data);
            return response.data;
        })
        .catch(error => {
            console.error('Error fetching group super sections:', error);
            return [];
        });
}
export const fetchSections = async (super_section_id) => {
    return httpService.get(`/api/libraries/super_sections/${super_section_id}/sections`)
        .then(response => {
            console.log('Fetched super section sections:', response.data);
            response.data.forEach(section => {
                section.tags = section.tags.map(tagObj => tags[tagObj - 1].name);
            });
            return response.data;
        })
        .catch(error => {
            console.error('Error fetching super section sections:', error);
            return [];
        });
}