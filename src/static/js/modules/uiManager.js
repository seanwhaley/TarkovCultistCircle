import config from './config.js';
import responseManager from './responseManager.js'; // Add missing import

class UiManager {
    constructor() {
        this.elements = {
            requestStatus: document.getElementById('request-status'),
            statusMessage: document.querySelector('#request-status .status-message'),
            graphqlResponse: document.getElementById('graphql-response'),
            responseSummary: document.getElementById('response-summary'),
            errorDetails: document.getElementById('error-details'),
            requestDetails: document.getElementById('request-details'),
            toggleWarning: document.getElementById('toggleWarning'),
            itemLimitControl: document.getElementById('itemLimitControl')
        };
        this.currentView = 'raw';
        this.currentRecordIndex = 0;
    }

    startRequest(message) {
        this.elements.requestStatus.style.display = 'flex';
        this.elements.statusMessage.textContent = message;
        this.elements.graphqlResponse.className = 'output-pre loading truncated';
    }

    updateRequestStatus(message) {
        this.elements.statusMessage.textContent = message;
    }

    endRequest() {
        this.elements.requestStatus.style.display = 'none';
    }

    async updateResponseDisplay(response, truncated = true, disableFullView = false) {
        if (!response) {
            this.elements.graphqlResponse.textContent = 'No response data available';
            this.elements.responseSummary.style.display = 'none';
            return;
        }

        const items = response?.details?.response?.data?.items || [];
        this.currentRecordIndex = Math.min(this.currentRecordIndex, items.length - 1);

        if (this.currentView === 'raw') {
            this.elements.graphqlResponse.textContent = JSON.stringify(response, null, 2);
            document.getElementById('recordNavigation').style.display = 'none';
        } else {
            if (items.length > 0) {
                this.elements.graphqlResponse.innerHTML = this.formatItemDisplay(items[this.currentRecordIndex]);
                document.getElementById('recordNavigation').style.display = 'flex';
                document.getElementById('recordCounter').textContent = 
                    `Record ${this.currentRecordIndex + 1} of ${items.length}`;
            } else {
                this.elements.graphqlResponse.textContent = 'No items found in response';
                document.getElementById('recordNavigation').style.display = 'none';
            }
        }

        // Update UI states
        this.elements.graphqlResponse.classList.toggle('truncated', truncated);
        
        // Toggle button visibility and state
        const toggleBtn = document.getElementById('toggleResponse');
        const toggleWarning = document.getElementById('toggleWarning');
        
        if (toggleBtn) {
            toggleBtn.disabled = disableFullView;
            toggleBtn.title = disableFullView ? 
                `Full view disabled for large responses (>${config.debug.maxFullViewItems} items)` : 
                'Toggle between full and truncated view';
        }
        
        if (toggleWarning) {
            toggleWarning.style.display = disableFullView ? 'flex' : 'none';
        }

        this.updateItemLimitVisibility(truncated);
        this.updateResponseSummary(response);
    }

    updateToggleWarning(show) {
        this.elements.toggleWarning.style.display = show ? 'flex' : 'none';
    }

    updateItemLimitVisibility(show) {
        this.elements.itemLimitControl.style.display = show ? 'block' : 'none';
    }

    showError(error) {
        this.elements.errorDetails.style.display = 'block';
        this.elements.errorDetails.querySelector('.details-content').innerHTML = `
            <p><strong>Error:</strong> ${error.message}</p>
            <p><strong>Type:</strong> ${error.name}</p>
        `;
    }

    resetUI() {
        this.elements.graphqlResponse.textContent = '';
        this.elements.responseSummary.style.display = 'none';
        this.elements.errorDetails.style.display = 'none';
        this.elements.requestDetails.style.display = 'none';
        this.elements.toggleWarning.style.display = 'none';
        this.endRequest();
        
        // Also reset neo4j preview
        const preview = document.getElementById('import-preview');
        if (preview) {
            preview.style.display = 'none';
            preview.querySelector('.preview-stats').innerHTML = '';
        }
    }

    updateResponseSummary(data) {
        const summary = document.getElementById('response-summary');
        if (!data?.details?.response?.data?.items) {
            summary.style.display = 'none';
            return;
        }
        
        const responseData = data.details.response.data;
        const items = responseData.items;
        const totalItems = responseData.totalCount || items.length;
        const displayCount = responseData.displayCount || items.length;
        
        try {
            const prices = items
                .map(i => parseInt(i.basePrice))
                .filter(p => !isNaN(p));
            
            const priceRange = prices.length ? `
                <div>Price Range (Current View): 
                    ${Math.min(...prices).toLocaleString()} - 
                    ${Math.max(...prices).toLocaleString()}
                </div>` : '';
            
            summary.style.display = 'block';
            summary.innerHTML = `
                <div class="summary-stats">
                    <div>Total Items: ${totalItems}</div>
                    <div>Showing: ${displayCount} items</div>
                    ${priceRange}
                </div>
            `;
        } catch (error) {
            console.error('Error calculating price range:', error);
            summary.innerHTML = `
                <div class="summary-stats">
                    <div>Total Items: ${totalItems}</div>
                    <div>Showing: ${displayCount} items</div>
                </div>
            `;
        }
    }

    generateSummaryHtml(items) {
        return `
            <div class="summary-stats">
                <div>Total Items: ${items.length}</div>
                <div>Price Range: ${Math.min(...items.map(i => i.basePrice))} - ${Math.max(...items.map(i => i.basePrice))}</div>
            </div>
        `;
    }

    showAlert(type, message) {
        const alert = document.getElementById('globalAlert');
        alert.className = `global-alert ${type}`;
        alert.textContent = message;
        alert.style.display = 'block';
        
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
    }

    formatDetails(details) {
        if (!details) return '';
        return Object.entries(details)
            .map(([key, value]) => this.generateDetailItemHtml(key, value))
            .join('');
    }

    generateDetailItemHtml(key, value) {
        return `
            <div class="detail-item">
                <strong>${key}:</strong> 
                <span>${JSON.stringify(value, null, 2)}</span>
            </div>
        `;
    }

    updateNeo4jStatus(response) {
        const status = document.getElementById('neo4j-status');
        const output = document.getElementById('neo4j-response');
        
        status.textContent = response.success ? 'Connected' : 'Error';
        status.className = response.success ? 'status-success' : 'status-error';
        
        output.textContent = JSON.stringify(response, null, 2);
        output.className = `output-pre ${response.success ? 'success' : 'error'}`;
    }

    showImportPreview(response) {
        const items = response?.details?.response?.data?.items;
        if (!items?.length) {
            console.error('Invalid response format for import preview');
            return;
        }

        try {
            const preview = document.getElementById('import-preview');
            const importButton = document.getElementById('importButton');
            
            preview.querySelector('.preview-stats').innerHTML = this.generatePreviewStats(items);
            preview.style.display = 'block';
            importButton.disabled = false;
        } catch (error) {
            console.error('Error showing import preview:', error);
            this.showAlert('error', 'Failed to display import preview');
        }
    }

    generatePreviewStats(items) {
        const totalValue = items.reduce((sum, item) => sum + (parseInt(item.basePrice) || 0), 0);
        
        return `
            <div class="preview-content">
                <p><strong>Items to Import:</strong> ${items.length}</p>
                <p><strong>Total Value:</strong> ${totalValue.toLocaleString()} ₽</p>
                <div class="sample-items">
                    <p><strong>Sample Items:</strong></p>
                    <ul>
                        ${items.slice(0, 5).map(item => 
                            `<li>${item.name} (${parseInt(item.basePrice).toLocaleString()} ₽)</li>`
                        ).join('')}
                    </ul>
                    ${items.length > 5 ? `<p>...and ${items.length - 5} more items</p>` : ''}
                </div>
            </div>
        `;
    }

    updateImportStatus(response) {
        const output = document.getElementById('neo4j-response');
        output.textContent = JSON.stringify(response, null, 2);
        output.className = `output-pre ${response.success ? 'success' : 'error'}`;
    }

    toggleResponseView(response, totalItems) {
        const pre = document.getElementById('graphql-response');
        const itemLimit = document.getElementById('itemLimitControl');
        const isCurrentlyTruncated = pre.classList.contains('truncated');
        
        pre.classList.toggle('truncated');
        itemLimit.style.display = isCurrentlyTruncated ? 'none' : 'block';
        
        const truncateLimit = isCurrentlyTruncated ? totalItems : parseInt(document.getElementById('itemLimit').value);
        const updatedResponse = responseManager.truncateResponseForDisplay(truncateLimit);
        this.updateResponseDisplay(updatedResponse, !isCurrentlyTruncated);
    }

    updateNeo4jPreview(response) {
        if (!response?.details?.response?.data?.items) return;
        
        try {
            const preview = document.getElementById('import-preview');
            const items = response.details.response.data.items;
            const totalItems = response.details.response.data.totalCount || items.length;
            
            preview.style.display = 'block';
            preview.querySelector('.preview-stats').innerHTML = `
                <p><strong>Total Items Available:</strong> ${totalItems}</p>
                <p><strong>Items Ready to Import:</strong> ${items.length}</p>
                <ul class="preview-list">
                    ${items.slice(0, 5).map(item => 
                        `<li>${item.name} (${parseInt(item.basePrice).toLocaleString()} ₽)</li>`
                    ).join('')}
                </ul>
                ${totalItems > 5 ? `<p>... and ${totalItems - 5} more items</p>` : ''}
                <p>Click 'Validate Import' to process all items</p>
            `;

            document.getElementById('importButton').disabled = false;
        } catch (error) {
            console.error('Error updating Neo4j preview:', error);
        }
    }

    formatItemDisplay(item) {
        return `
            <div class="item-card">
                <header class="item-header">
                    <h4>${item.name}</h4>
                    ${item.iconLink ? `<img src="${item.iconLink}" alt="${item.name}" class="item-icon"/>` : ''}
                </header>
                
                <div class="item-details">
                    <div class="price-info">
                        <h5>Pricing</h5>
                        <p><strong>Base Price:</strong> ${parseInt(item.basePrice).toLocaleString()} ₽</p>
                        ${item.fleaMarketFee ? 
                            `<p><strong>Flea Market Fee:</strong> ${parseInt(item.fleaMarketFee).toLocaleString()} ₽</p>` : ''}
                        ${item.weight ? 
                            `<p><strong>Weight:</strong> ${item.weight} kg</p>` : ''}
                    </div>
                    
                    <div class="trader-prices">
                        <h5>Trader Information</h5>
                        ${this.formatTraderPrices(item.buyFor, item.sellFor)}
                    </div>
                    
                    <div class="categories">
                        <h5>Categories</h5>
                        <p>${item.categories.map(c => c.name).join(', ')}</p>
                    </div>
                    
                    <footer class="item-footer">
                        <div class="last-updated">
                            <small>Last Updated: ${new Date(item.updated).toLocaleString()}</small>
                        </div>
                        ${item.wikiLink ? 
                            `<a href="${item.wikiLink}" target="_blank" class="wiki-link">
                                <span class="material-icons">open_in_new</span> Wiki
                             </a>` : ''}
                    </footer>
                </div>
            </div>
        `;
    }

    formatTraderPrices(buyPrices, sellPrices) {
        const traders = new Map();
        
        // Combine buy and sell prices by trader
        buyPrices?.forEach(bp => {
            if (!traders.has(bp.vendor.name)) {
                traders.set(bp.vendor.name, { buy: bp.priceRUB });
            } else {
                traders.get(bp.vendor.name).buy = bp.priceRUB;
            }
        });
        
        sellPrices?.forEach(sp => {
            if (!traders.has(sp.vendor.name)) {
                traders.set(sp.vendor.name, { sell: sp.priceRUB });
            } else {
                traders.get(sp.vendor.name).sell = sp.priceRUB;
            }
        });

        return `
            <table class="trader-prices-table">
                <tr>
                    <th>Trader</th>
                    <th>Buy</th>
                    <th>Sell</th>
                    <th>Profit</th>
                </tr>
                ${Array.from(traders.entries()).map(([name, prices]) => `
                    <tr>
                        <td>${name}</td>
                        <td>${prices.buy ? parseInt(prices.buy).toLocaleString() + ' ₽' : '-'}</td>
                        <td>${prices.sell ? parseInt(prices.sell).toLocaleString() + ' ₽' : '-'}</td>
                        <td>${this.calculateProfit(prices)}</td>
                    </tr>
                `).join('')}
            </table>
        `;
    }

    calculateProfit({ buy, sell }) {
        if (!buy || !sell) return '-';
        const profit = parseInt(sell) - parseInt(buy);
        return `${profit.toLocaleString()} ₽`;
    }

    setResponseView(viewType) {
        this.currentView = viewType;
        
        // Update button states
        document.getElementById('viewToggleRaw').classList.toggle('active', viewType === 'raw');
        document.getElementById('viewToggleFormatted').classList.toggle('active', viewType === 'formatted');
        
        // Show/hide navigation based on view type
        document.getElementById('recordNavigation').style.display = 
            viewType === 'formatted' ? 'flex' : 'none';
        
        // Re-render current response
        const response = responseManager.getResponse();
        if (response) {
            this.updateResponseDisplay(response);
        }

        // Update UI visibility
        document.getElementById('itemLimitControl').style.display = 
            viewType === 'raw' ? 'block' : 'none';
    }

    nextRecord() {
        const items = responseManager.getResponse()?.details?.response?.data?.items || [];
        if (items.length > 0) {
            this.currentRecordIndex = (this.currentRecordIndex + 1) % items.length;
            this.updateResponseDisplay(responseManager.getResponse());
        }
    }

    previousRecord() {
        const items = responseManager.getResponse()?.details?.response?.data?.items || [];
        if (items.length > 0) {
            this.currentRecordIndex = (this.currentRecordIndex - 1 + items.length) % items.length;
            this.updateResponseDisplay(responseManager.getResponse());
        }
    }
}

export default new UiManager();
