class ResponseManager {
    constructor() {
        this.response = null;
        this.currentRequest = null;
        this.requestTimeout = null;
    }

    setResponse(response) {
        console.log('Setting response:', {
            hasData: !!response,
            itemCount: response?.details?.response?.data?.items?.length
        });
        this.response = response;
    }

    getResponse() {
        console.log('Getting response:', {
            hasData: !!this.response,
            itemCount: this.response?.details?.response?.data?.items?.length
        });
        return this.response;
    }

    truncateResponseForDisplay(forcedLimit = null) {
        if (!this.response?.details?.response?.data?.items) return this.response;
        
        const items = this.response.details.response.data.items;
        const totalItems = items.length;
        const itemLimit = forcedLimit || parseInt(document.getElementById('itemLimit').value) || 5;
        
        return {
            ...this.response,
            details: {
                response: {
                    data: {
                        items: items.slice(0, itemLimit),
                        totalCount: totalItems,
                        displayCount: Math.min(itemLimit, totalItems),
                        _truncated: itemLimit < totalItems
                    }
                }
            }
        };
    }

    clear() {
        this.response = null;
        this.cancelCurrentRequest();
    }

    cancelCurrentRequest() {
        if (this.currentRequest) {
            this.currentRequest.abort();
            this.currentRequest = null;
        }
        if (this.requestTimeout) {
            clearTimeout(this.requestTimeout);
            this.requestTimeout = null;
        }
    }
}

export default new ResponseManager();
