// Notification System
function showNotify(msg, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

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
}

document.addEventListener('DOMContentLoaded', () => {
    // Add toast container if not exists
    if (!document.getElementById('toast-container')) {
        const tc = document.createElement('div');
        tc.id = 'toast-container';
        tc.className = 'toast-container';
        document.body.appendChild(tc);
    }

    const form = document.querySelector('#tailor-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const masterJson = document.querySelector('#master_json').value;
            const jd = document.querySelector('#jd').value;
            const loading = document.getElementById('loading');

            // Simple validation
            try {
                JSON.parse(masterJson);
            } catch (err) {
                showNotify('Invalid JSON format in Master Resume data.', 'error');
                return;
            }

            loading.style.display = 'flex';

            const formData = new FormData();
            formData.append('master_json', masterJson);
            formData.append('jd', jd);

            try {
                const response = await fetch('/api/tailor', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (result.success) {
                    sessionStorage.setItem('tailored_resume', JSON.stringify(result));
                    sessionStorage.setItem('ats_score', result.score);
                    window.location.href = 'result.html';
                } else {
                    showNotify('Tailoring failed: ' + result.error, 'error');
                }
            } catch (error) {
                console.error('Submission failed:', error);
                showNotify('Technical error. Please try again.', 'error');
            } finally {
                loading.style.display = 'none';
            }
        });
    }
});
