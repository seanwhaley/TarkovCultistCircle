import responseManager from './responseManager.js';
import apiService from './apiService.js';
import uiManager from './uiManager.js';
import config from './config.js';

class DebugController {
    constructor() {
        this.initializeEventHandlers();
    }

    initializeEventHandlers() {
        // Bind all methods to window for onclick handlers
        window.showTab = this.showTab.bind(this);
        window.testGraphQL = this.testGraphQL.bind(this);
        window.loadLastResponse = this.loadLastResponse.bind(this);
        window.testNeo4j = this.testNeo4j.bind(this);
        window.validateImport = this.validateImport.bind(this);
        window.importLastResponse = this.importLastResponse.bind(this);
        window.toggleFullResponse = this.toggleFullResponse.bind(this);
        window.updateResponseDisplay = this.updateResponseDisplay.bind(this);
        window.cancelRequest = this.cancelRequest.bind(this);
        
        // Add missing view toggle handlers
        window.toggleResponseView = this.toggleResponseView.bind(this);
        window.previousRecord = this.previousRecord.bind(this);
        window.nextRecord = this.nextRecord.bind(this);
        
        // Add keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (document.activeElement.tagName !== 'INPUT') {
                if (e.key === 'ArrowLeft') this.previousRecord();
                if (e.key === 'ArrowRight') this.nextRecord();
            }
        });
    }

    showTab(tabName) {
        if (tabName === 'neo4j') {
            const currentResponse = responseManager.getResponse();
            
            // Don't clear response when switching to Neo4j tab
            uiManager.resetUI();
            
            const noDataMessage = document.getElementById('no-data-message');
            const importPreview = document.getElementById('import-preview');
            
            if (currentResponse?.details?.response?.data?.items) {
                noDataMessage.style.display = 'none';
                importPreview.style.display = 'block';
                uiManager.updateNeo4jPreview(currentResponse);
            } else {
                noDataMessage.style.display = 'block';
                importPreview.style.display = 'none';
            }
        } else if (tabName === 'graphql') {
            // Only clear UI, keep response data
            uiManager.resetUI();
        }
        
        // Update tab visibility
        document.querySelectorAll('.tab-content').forEach(tab => 
            tab.classList.remove('active'));
        document.querySelectorAll('.tab-button').forEach(btn => 
            btn.classList.remove('active'));
        
        document.getElementById(`${tabName}-tab`).classList.add('active');
        document.querySelector(`button[onclick="showTab('${tabName}')"]`)
            .classList.add('active');
    }

    async testGraphQL() {
        uiManager.startRequest('Sending GraphQL request...');
        try {
            const response = await apiService.fetchGraphQL('/api/fetch_graphql', {
                method: 'POST'
            });
            
            const normalizedResponse = this.normalizeResponse(response);
            responseManager.setResponse(normalizedResponse);
            
            const totalItems = normalizedResponse.details?.response?.data?.items?.length || 0;
            const truncatedResponse = responseManager.truncateResponseForDisplay();
            
            await uiManager.updateResponseDisplay(truncatedResponse, true, totalItems > config.debug.maxFullViewItems);
            uiManager.showAlert('success', 'Successfully fetched data');
        } catch (error) {
            console.error('GraphQL request failed:', error);
            uiManager.showAlert('error', error.message);
            uiManager.showError(error);
        } finally {
            uiManager.endRequest();
        }
    }

    async loadLastResponse() {
        console.log('1. Starting loadLastResponse...');
        try {
            const response = await apiService.fetchGraphQL('/api/load_last_response');
            const normalizedResponse = this.normalizeResponse(response);
            
            responseManager.setResponse(normalizedResponse);
            const truncatedResponse = responseManager.truncateResponseForDisplay();
            await uiManager.updateResponseDisplay(truncatedResponse, true);
            
            uiManager.showAlert('success', 'Response loaded successfully');
        } catch (error) {
            console.error('LoadLastResponse error:', error);
            uiManager.showAlert('error', error.message);
        }
    }

    // Add helper method to normalize response structure
    normalizeResponse(response) {
        console.log('Normalizing response:', response);

        // Handle response with details.request structure
        if (response?.details?.request?.data?.items) {
            console.log('Converting request details format');
            return {
                success: true,
                details: {
                    response: {
                        data: {
                            items: response.details.request.data.items,
                            totalCount: response.details.request.data.items.length
                        }
                    }
                }
            };
        }

        // Handle response with details.response structure
        if (response?.details?.response?.data?.items) {
            console.log('Response already in correct format');
            return response;
        }

        // Handle the new response format where data is nested in response.response
        if (response?.response?.data?.items) {
            console.log('Converting nested response format');
            return {
                success: true,
                details: {
                    response: {
                        data: {
                            items: response.response.data.items,
                            totalCount: response.response.data.items.length
                        }
                    }
                }
            };
        }

        // Handle legacy format where data is directly in response
        if (response?.data?.items) {
            console.log('Converting direct data format');
            return {
                success: true,
                details: {
                    response: {
                        data: {
                            items: response.data.items,
                            totalCount: response.data.items.length
                        }
                    }
                }
            };
        }

        console.error('Response structure analysis:', {
            hasDetails: !!response?.details,
            hasRequest: !!response?.details?.request,
            hasResponse: !!response?.details?.response,
            hasData: !!response?.data,
            structure: {
                topLevel: Object.keys(response || {}),
                details: Object.keys(response?.details || {}),
                request: Object.keys(response?.details?.request || {}),
                response: Object.keys(response?.details?.response || {})
            }
        });
        
        throw new Error('Unable to normalize response structure');
    }

    async testNeo4j() {
        try {
            const response = await apiService.fetchGraphQL('/api/test_neo4j');
            uiManager.updateNeo4jStatus(response);
        } catch (error) {
            uiManager.showAlert('error', error.message);
        }
    }

    validateItemFormat(item) {
        const requiredFields = {
            id: 'string',
            name: 'string',
            basePrice: 'number',
            updated: 'string',
            weight: 'number'
        };
        
        const issues = [];
        for (const [field, type] of Object.entries(requiredFields)) {
            if (!item[field]) {
                issues.push(`Missing ${field}`);
            } else if (typeof item[field] !== type) {
                issues.push(`Invalid type for ${field}: expected ${type}, got ${typeof item[field]}`);
            }
        }
        return issues;
    }

    async validateImport() {
        try {
            const response = responseManager.getResponse();
            console.log('Validating import with response:', response);

            if (!response?.details?.response?.data?.items) {
                throw new Error('No item data available. Please fetch or load data first.');
            }

            const items = response.details.response.data.items;
            console.log(`Found ${items.length} items to validate`);

            // Validate first 5 items in detail
            const validationIssues = items.slice(0, 5).map(item => ({
                name: item.name,
                issues: this.validateItemFormat(item)
            })).filter(result => result.issues.length > 0);

            if (validationIssues.length > 0) {
                console.error('Validation issues found:', validationIssues);
                throw new Error(`Data validation failed. Check console for details.`);
            }

            uiManager.showImportPreview({
                details: {
                    response: {
                        data: { items }
                    }
                }
            });
            
            uiManager.showAlert('success', 
                `Validated ${items.length} items. Sample data looks correct for Neo4j import.`);
        } catch (error) {
            console.error('Validate import error:', error);
            uiManager.showAlert('error', error.message);
        }
    }

    async importLastResponse() {
        try {
            const response = await apiService.importData('/api/import_last_response');
            uiManager.updateImportStatus(response);
        } catch (error) {
            uiManager.showAlert('error', error.message);
        }
    }

    toggleFullResponse() {
        const response = responseManager.getResponse(); // Changed from getFullResponse
        if (!response) return;
        
        const totalItems = response.details?.response?.data?.items?.length || 0;
        if (totalItems > config.debug.maxFullViewItems) {
            uiManager.showAlert('warning', 
                `Full view disabled for large responses (>${config.debug.maxFullViewItems} items)`);
            return;
        }
        
        uiManager.toggleResponseView(response, totalItems);
    }

    updateResponseDisplay() {
        const response = responseManager.getResponse(); // Changed from getFullResponse
        if (!response) return;
        
        // Always use truncated response when updating display from dropdown
        const truncatedResponse = responseManager.truncateResponseForDisplay();
        uiManager.updateResponseDisplay(truncatedResponse, true);
    }

    cancelRequest() {
        responseManager.cancelCurrentRequest();
        uiManager.showAlert('info', 'Request cancelled');
    }

    cleanup() {
        responseManager.clear(); // Changed from clearResponses
        uiManager.resetUI();
    }

    toggleResponseView(viewType) {
        uiManager.setResponseView(viewType);
    }

    previousRecord() {
        uiManager.previousRecord();
    }

    nextRecord() {
        uiManager.nextRecord();
    }
}

export default new DebugController();
