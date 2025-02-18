class ApiService {
    async fetchGraphQL(url, options = {}) {
        console.log('API: Starting fetch request to:', url);
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            console.log('API: Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('API: Response data structure:', {
                hasData: !!data,
                keys: Object.keys(data || {})
            });
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            if (error.name === 'AbortError') {
                throw new Error('Request timed out after 30 seconds');
            }
            throw error;
        } finally {
            clearTimeout(timeoutId);
        }
    }

    async testNeo4j(url) {
        return await this.fetchGraphQL(url);
    }

    async importData(url, data) {
        return await this.fetchGraphQL(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
    }
}

export default new ApiService();
