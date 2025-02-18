class UIEnhancer {
    constructor() {
        this.initializeSections();
        this.initializeKeyboardShortcuts();
        this.initializeDensityControls();
        this.restoreUserPreferences();
    }

    initializeSections() {
        document.querySelectorAll('.collapsible-section').forEach(section => {
            const header = section.querySelector('.section-header');
            const content = section.querySelector('.section-content');
            const toggle = section.querySelector('.section-toggle');

            if (header && content) {
                header.addEventListener('click', () => this.toggleSection(section));
                header.addEventListener('dblclick', (e) => {
                    e.stopPropagation();
                    this.toggleAllSections();
                });
            }

            // Restore section state
            const sectionId = section.id || section.querySelector('h2,h3,h4')?.textContent;
            if (sectionId) {
                const isCollapsed = localStorage.getItem(`section-${sectionId}`) === 'true';
                if (isCollapsed) {
                    content.classList.add('collapsed');
                    toggle?.classList.add('collapsed');
                }
            }
        });
    }

    toggleSection(section) {
        const content = section.querySelector('.section-content');
        const toggle = section.querySelector('.section-toggle');
        const sectionId = section.id || section.querySelector('h2,h3,h4')?.textContent;

        content.classList.toggle('collapsed');
        toggle?.classList.toggle('collapsed');

        if (sectionId) {
            localStorage.setItem(`section-${sectionId}`, 
                content.classList.contains('collapsed'));
        }
    }

    toggleAllSections() {
        const sections = document.querySelectorAll('.collapsible-section');
        const allCollapsed = Array.from(sections)
            .every(s => s.querySelector('.section-content')?.classList.contains('collapsed'));

        sections.forEach(section => {
            const content = section.querySelector('.section-content');
            if (content?.classList.contains('collapsed') !== !allCollapsed) {
                this.toggleSection(section);
            }
        });
    }

    initializeKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Alt+C to collapse all sections
            if (e.altKey && e.key === 'c') {
                e.preventDefault();
                this.toggleAllSections();
            }
            
            // Add more keyboard shortcuts here
        });
    }

    initializeDensityControls() {
        const densitySelect = document.querySelector('.density-select');
        if (densitySelect) {
            densitySelect.addEventListener('change', (e) => {
                this.setDensity(e.target.value);
            });
        }
    }

    setDensity(density) {
        document.body.dataset.density = density;
        localStorage.setItem('viewDensity', density);
    }

    restoreUserPreferences() {
        const savedDensity = localStorage.getItem('viewDensity');
        if (savedDensity) {
            this.setDensity(savedDensity);
            const densitySelect = document.querySelector('.density-select');
            if (densitySelect) {
                densitySelect.value = savedDensity;
            }
        }
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.uiEnhancer = new UIEnhancer();
});
