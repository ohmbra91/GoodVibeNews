import axios from 'axios';

const API_BASE_URL = 'https://goodvibenews.live'; // Update to use your new domain

export const fetchArticles = async () => {
    const response = await axios.get(`${API_BASE_URL}/api/articles`);
    return response.data;
};