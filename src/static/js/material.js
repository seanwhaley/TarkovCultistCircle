// Material Design Ripple Effect
class MDRipple {
    constructor(element) {
        this.element = element;
        this.element.style.position = 'relative';
        this.element.style.overflow = 'hidden';
        this.bindEvents();
    }

    bindEvents() {
        this.element.addEventListener('mousedown', e => this.createRipple(e));
    }

    createRipple(event) {
        const ripple = document.createElement('span');
        const rect = this.element.getBoundingClientRect();
        
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            top: ${y}px;
            left: ${x}px;
            background-color: currentColor;
            border-radius: 50%;
            opacity: 0.2;
            transform: scale(0);
            transition: transform 0.6s, opacity 0.6s;
            pointer-events: none;
        `;
        
        this.element.appendChild(ripple);
        requestAnimationFrame(() => {
            ripple.style.transform = 'scale(2)';
            ripple.style.opacity = '0';
        });
        
        setTimeout(() => ripple.remove(), 600);
    }

    static attach(element) {
        return new MDRipple(element);
    }
}

// Material Design Menu
class MDMenu {
    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            position: 'bottom-start',
            offset: 8,
            ...options
        };
        this.init();
    }

    init() {
        this.element.style.position = 'absolute';
        this.element.style.opacity = '0';
        this.element.style.visibility = 'hidden';
        this.element.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
    }

    open(target) {
        const targetRect = target.getBoundingClientRect();
        const menuRect = this.element.getBoundingClientRect();
        
        let x = 0;
        let y = 0;
        
        switch (this.options.position) {
            case 'bottom-start':
                x = targetRect.left;
                y = targetRect.bottom + this.options.offset;
                break;
            case 'bottom-end':
                x = targetRect.right - menuRect.width;
                y = targetRect.bottom + this.options.offset;
                break;
        }
        
        this.element.style.left = `${x}px`;
        this.element.style.top = `${y}px`;
        this.element.style.opacity = '1';
        this.element.style.visibility = 'visible';
        this.element.style.transform = 'scale(1)';
        
        const closeOnClick = e => {
            if (!this.element.contains(e.target) && e.target !== target) {
                this.close();
                document.removeEventListener('click', closeOnClick);
            }
        };
        
        document.addEventListener('click', closeOnClick);
    }

    close() {
        this.element.style.opacity = '0';
        this.element.style.visibility = 'hidden';
        this.element.style.transform = 'scale(0.8)';
    }
}

// Material Design Bottom Sheet
class MDBottomSheet {
    constructor(element) {
        this.element = element;
        this.init();
    }

    init() {
        this.element.style.transform = 'translateY(100%)';
        this.element.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        
        const overlay = document.createElement('div');
        overlay.className = 'bottom-sheet-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease;
            z-index: 999;
        `;
        
        document.body.appendChild(overlay);
        this.overlay = overlay;
        
        this.overlay.addEventListener('click', () => this.close());
    }

    open() {
        this.element.style.transform = 'translateY(0)';
        this.overlay.style.opacity = '1';
        this.overlay.style.visibility = 'visible';
    }

    close() {
        this.element.style.transform = 'translateY(100%)';
        this.overlay.style.opacity = '0';
        this.overlay.style.visibility = 'hidden';
    }
}

// Material Design Snackbar
class MDSnackbar {
    constructor(options = {}) {
        this.options = {
            duration: 4000,
            position: 'bottom-center',
            ...options
        };
        this.init();
    }

    init() {
        this.container = document.createElement('div');
        this.container.className = 'snackbar-container';
        this.container.style.cssText = `
            position: fixed;
            z-index: 1000;
            pointer-events: none;
        `;
        
        switch (this.options.position) {
            case 'bottom-center':
                this.container.style.bottom = '24px';
                this.container.style.left = '50%';
                this.container.style.transform = 'translateX(-50%)';
                break;
        }
        
        document.body.appendChild(this.container);
    }

    show(message, action) {
        const snackbar = document.createElement('div');
        snackbar.className = 'snackbar';
        snackbar.style.cssText = `
            background-color: var(--md-surface);
            color: var(--md-on-surface);
            padding: 14px 16px;
            border-radius: 4px;
            box-shadow: var(--md-elevation-2);
            display: flex;
            align-items: center;
            justify-content: space-between;
            min-width: 288px;
            max-width: 568px;
            margin: 8px;
            pointer-events: auto;
            transform: scale(0.8);
            opacity: 0;
            transition: transform 0.2s ease, opacity 0.2s ease;
        `;
        
        const messageEl = document.createElement('span');
        messageEl.textContent = message;
        snackbar.appendChild(messageEl);
        
        if (action) {
            const button = document.createElement('button');
            button.className = 'btn text-uppercase ms-3';
            button.style.color = 'var(--md-primary)';
            button.textContent = action.text;
            button.addEventListener('click', action.handler);
            snackbar.appendChild(button);
        }
        
        this.container.appendChild(snackbar);
        
        requestAnimationFrame(() => {
            snackbar.style.transform = 'scale(1)';
            snackbar.style.opacity = '1';
        });
        
        setTimeout(() => {
            snackbar.style.transform = 'scale(0.8)';
            snackbar.style.opacity = '0';
            setTimeout(() => snackbar.remove(), 200);
        }, this.options.duration);
    }
}

// Material Design Dialog
class MDDialog {
    constructor(options = {}) {
        this.options = {
            persistent: false,
            ...options
        };
    }

    static create(options = {}) {
        const dialog = document.createElement('div');
        dialog.className = 'dialog';
        dialog.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: rgba(0, 0, 0, 0.5);
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.2s ease;
            z-index: 1000;
        `;
        
        const content = document.createElement('div');
        content.className = 'dialog-content surface';
        content.style.cssText = `
            background-color: var(--md-surface);
            color: var(--md-on-surface);
            border-radius: 4px;
            padding: 24px;
            max-width: 560px;
            width: 90%;
            transform: scale(0.8);
            transition: transform 0.2s ease;
            box-shadow: var(--md-elevation-4);
        `;
        
        dialog.appendChild(content);
        document.body.appendChild(dialog);
        
        return {
            element: dialog,
            content: content,
            show() {
                dialog.style.opacity = '1';
                dialog.style.visibility = 'visible';
                content.style.transform = 'scale(1)';
            },
            hide() {
                dialog.style.opacity = '0';
                dialog.style.visibility = 'hidden';
                content.style.transform = 'scale(0.8)';
            }
        };
    }
}

// Export Material Design components
window.MD = {
    Ripple: MDRipple,
    Menu: MDMenu,
    BottomSheet: MDBottomSheet,
    Snackbar: MDSnackbar,
    Dialog: MDDialog
};