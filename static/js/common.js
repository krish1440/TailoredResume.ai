/**
 * common.js - Shared utilities for TailoredResume.ai
 */

document.addEventListener('DOMContentLoaded', () => {
    // Back to Top functionality
    const backToTop = document.getElementById('back-to-top');
    if (backToTop) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 400) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        });

        backToTop.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Shared notification helper (if not already defined)
    if (typeof showNotify === 'undefined') {
        window.showNotify = (msg, type = 'success') => {
            const container = document.getElementById('toast-container') || createToastContainer();
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.innerHTML = `
                <span style="font-size:1.2rem;">${type === 'success' ? '✅' : '❌'}</span>
                <span>${msg}</span>
            `;
            container.appendChild(toast);
            setTimeout(() => {
                toast.style.animation = 'fadeOut 0.3s forwards';
                setTimeout(() => toast.remove(), 300);
            }, 4000);
        };
    }

    function createToastContainer() {
        const tc = document.createElement('div');
        tc.id = 'toast-container';
        tc.className = 'toast-container';
        document.body.appendChild(tc);
        return tc;
    }
});
/**
 * Copies text to clipboard and shows a notification.
 * @param {string} text - The string to copy.
 * @param {string} successMsg - Message to show on success.
 */
window.copyText = (text, successMsg = 'Copied to clipboard!') => {
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
        if (typeof showNotify === 'function') {
            showNotify(successMsg);
        } else {
            alert(successMsg);
        }
    }).catch(err => {
        console.error('Copy failed:', err);
        if (typeof showNotify === 'function') {
            showNotify('Failed to copy text', 'error');
        }
    });
};
