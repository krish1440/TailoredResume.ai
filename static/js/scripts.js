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
                    sessionStorage.setItem('ats_metrics', JSON.stringify(result.metrics || {}));
                    window.location.href = '/result';
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

    // Bi-directional Sync
    document.getElementById('tailor-form').addEventListener('input', (e) => {
        if (e.target.closest('#builder-container')) {
            syncFormToJson();
        }
    });

    // Initialize with EMPTY items (NOT samples)
    if (document.getElementById('builder-container')) {
        addItem('summaries');
        addItem('experience');
        addItem('projects');
        addItem('education');
        addItem('skills');
    }
});

function switchTab(target) {
    const builder = document.getElementById('builder-container');
    const jsonContainer = document.getElementById('json-container');
    const btns = document.querySelectorAll('.tab-btn');

    btns.forEach(b => b.classList.remove('active'));
    
    if (target === 'form') {
        builder.style.display = 'block';
        jsonContainer.style.display = 'none';
        btns[0].classList.add('active');
        syncJsonToForm();
    } else {
        builder.style.display = 'none';
        jsonContainer.style.display = 'block';
        btns[1].classList.add('active');
        syncFormToJson();
    }
}

function syncFormToJson() {
    const data = {
        personal_info: {},
        professional_summaries: [],
        skills: {},
        experience: [],
        projects: [],
        education: []
    };

    // Personal Info
    document.querySelectorAll('[data-path^="personal_info."]').forEach(input => {
        const key = input.dataset.path.split('.')[1];
        data.personal_info[key] = input.value;
    });

    // Professional Summaries
    document.querySelectorAll('.summary-item textarea').forEach(textarea => {
        if (textarea.value.trim()) data.professional_summaries.push(textarea.value.trim());
    });

    // Skills
    document.querySelectorAll('.skill-group').forEach(group => {
        const cat = group.querySelector('.skill-cat').value || 'skills';
        const items = group.querySelector('.skill-items').value.split(',').map(s => s.trim()).filter(s => s);
        data.skills[cat] = items;
    });

    // Experience
    document.querySelectorAll('.experience-item').forEach(item => {
        const entry = {};
        item.querySelectorAll('[data-field]').forEach(input => {
            const field = input.dataset.field;
            if (field === 'bullet_points') {
                entry[field] = Array.from(item.querySelectorAll('.bullet-input')).map(bi => bi.value.trim()).filter(v => v);
            } else {
                entry[field] = input.value;
            }
        });
        data.experience.push(entry);
    });

    // Projects
    document.querySelectorAll('.projects-item').forEach(item => {
        const entry = {
            name: item.querySelector('[data-field="name"]').value,
            tech_stack: item.querySelector('[data-field="tech_stack"]').value.split(',').map(t => t.trim()).filter(t => t),
            master_narrative: item.querySelector('[data-field="master_narrative"]').value,
            quantified_impact: Array.from(item.querySelectorAll('.impact-input')).map(i => i.value.trim()).filter(v => v),
            core_actions: Array.from(item.querySelectorAll('.action-input')).map(i => i.value.trim()).filter(v => v)
        };
        data.projects.push(entry);
    });

    // Education
    document.querySelectorAll('.education-item').forEach(item => {
        const entry = {};
        item.querySelectorAll('[data-field]').forEach(input => {
            entry[input.dataset.field] = input.value;
        });
        data.education.push(entry);
    });

    document.getElementById('master_json').value = JSON.stringify(data, null, 2);
}

function syncJsonToForm() {
    try {
        const data = JSON.parse(document.getElementById('master_json').value);
        
        // Personal Info
        Object.entries(data.personal_info || {}).forEach(([key, val]) => {
            const input = document.querySelector(`[data-path="personal_info.${key}"]`);
            if (input) input.value = val;
        });

        // Lists
        document.getElementById('summaries-list').innerHTML = '';
        document.getElementById('experience-list').innerHTML = '';
        document.getElementById('projects-list').innerHTML = '';
        document.getElementById('education-list').innerHTML = '';
        document.getElementById('skills-list').innerHTML = '';

        (data.professional_summaries || []).forEach(s => addItem('summaries', s));
        (data.experience || []).forEach(exp => addItem('experience', exp));
        (data.projects || []).forEach(proj => addItem('projects', proj));
        (data.education || []).forEach(edu => addItem('education', edu));
        Object.entries(data.skills || {}).forEach(([cat, items]) => addItem('skills', {cat, items}));

    } catch (e) { console.warn("Sync failed: Invalid JSON"); }
}

function addItem(type, data = null) {
    const list = document.getElementById(`${type}-list`);
    const div = document.createElement('div');
    div.className = `${type}-item card`;
    div.style.marginBottom = '1.5rem';
    div.style.padding = '1.5rem';

    let html = '';
    if (type === 'summaries') {
        html = `<textarea class="input-field" placeholder="Professional Summary Option" rows="3">${data || ''}</textarea>`;
    } else if (type === 'experience') {
        html = `
            <div class="form-row">
                <input type="text" class="input-field" placeholder="Company Name" data-field="company" value="${data?.company || ''}" required>
                <input type="text" class="input-field" placeholder="Role Title" data-field="role" value="${data?.role || ''}" required>
            </div>
            <div class="form-row">
                <input type="text" class="input-field" placeholder="Start Date" data-field="start_date" value="${data?.start_date || ''}" required>
                <input type="text" class="input-field" placeholder="End Date" data-field="end_date" value="${data?.end_date || ''}" required>
            </div>
            <div class="bullet-container">
                <label style="font-size:0.85rem">Experience Bullets (Min 3 Required)*</label>
                <div class="bullets-list">
                    ${(data?.bullet_points || ["", "", ""]).map((bp, i) => `
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:5px">
                            <span style="font-size:0.75rem; color:var(--text-secondary); width:15px">${i+1}.</span>
                            <input type="text" class="input-field bullet-input" placeholder="Bullet Point" value="${bp}" ${i < 3 ? 'required' : ''}>
                        </div>
                    `).join('')}
                </div>
                <button type="button" class="btn btn-secondary" onclick="addNestedInput(this, 'bullet-input', 'Bullet Point')" style="font-size:0.75rem; padding:5px 12px; margin-top:5px; border-radius:20px">+ Add More Bullets</button>
            </div>
        `;
    } else if (type === 'projects') {
        html = `
            <div class="form-row">
                <input type="text" class="input-field" placeholder="Project Name" data-field="name" value="${data?.name || ''}" required>
                <input type="text" class="input-field" placeholder="Tech Stack" data-field="tech_stack" value="${(data?.tech_stack || []).join(', ')}" required>
            </div>
            <div style="margin-top:1rem">
                <label style="font-size:0.85rem">Master Narrative*</label>
                <textarea class="input-field" data-field="master_narrative" placeholder="Detailed story of your project" rows="4" required>${data?.master_narrative || ''}</textarea>
            </div>
            <div class="form-row" style="margin-top:1rem">
                <div>
                    <label style="font-size:0.85rem; display:block; margin-bottom:0.5rem">Quantified Impacts (Min 3 Required)*</label>
                    <div class="impacts-list">
                        ${(data?.quantified_impact || ["", "", ""]).map((i, idx) => `
                            <div style="display:flex; align-items:center; gap:8px; margin-bottom:5px">
                                <span style="font-size:0.75rem; color:var(--text-secondary); width:15px">${idx+1}.</span>
                                <input type="text" class="input-field impact-input" placeholder="Quantified Impact" value="${i}" ${idx < 3 ? 'required' : ''}>
                            </div>
                        `).join('')}
                    </div>
                    <button type="button" class="btn btn-secondary" onclick="addNestedInput(this, 'impact-input', 'Quantified Impact')" style="font-size:0.75rem; padding:5px 12px; margin-top:5px; border-radius:20px">+ Add Impact</button>
                </div>
                <div>
                    <label style="font-size:0.85rem; display:block; margin-bottom:0.5rem">Core Actions (Min 3 Required)*</label>
                    <div class="actions-list">
                        ${(data?.core_actions || ["", "", ""]).map((a, idx) => `
                            <div style="display:flex; align-items:center; gap:8px; margin-bottom:5px">
                                <span style="font-size:0.75rem; color:var(--text-secondary); width:15px">${idx+1}.</span>
                                <input type="text" class="input-field action-input" placeholder="Technical Core Action" value="${a}" ${idx < 3 ? 'required' : ''}>
                            </div>
                        `).join('')}
                    </div>
                    <button type="button" class="btn btn-secondary" onclick="addNestedInput(this, 'action-input', 'Technical Core Action')" style="font-size:0.75rem; padding:5px 12px; margin-top:5px; border-radius:20px">+ Add Action</button>
                </div>
            </div>
        `;
    } else if (type === 'education') {
        html = `
            <input type="text" class="input-field" placeholder="Institution Name" data-field="institution" value="${data?.institution || ''}" required style="margin-bottom:1rem">
            <div class="form-row">
                <input type="text" class="input-field" placeholder="Degree Type" data-field="degree" value="${data?.degree || ''}" required>
                <input type="text" class="input-field" placeholder="GPA / CGPA" data-field="gpa" value="${data?.gpa || ''}" required>
            </div>
            <div class="form-row" style="margin-top:10px">
                <input type="text" class="input-field" placeholder="Start Year" data-field="start_date" value="${data?.start_date || ''}" required>
                <input type="text" class="input-field" placeholder="End Year" data-field="end_date" value="${data?.end_date || ''}" required>
            </div>
        `;
    } else if (type === 'skills') {
        div.className = 'skill-group card';
        html = `
            <div style="display: flex; flex-direction: column; gap: 0.8rem;">
                <div>
                    <label style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.4rem; display: block;">Skill Domain (e.g. Languages)*</label>
                    <input type="text" class="input-field skill-cat" placeholder="Skill Domain" value="${data?.cat || ''}" required>
                </div>
                <div>
                    <label style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.4rem; display: block;">List of Skills*</label>
                    <input type="text" class="input-field skill-items" placeholder="List of Skills" value="${(data?.items || []).join(', ')}" required>
                </div>
            </div>
        `;
    }

    div.innerHTML = html + `<button type="button" class="remove-btn" onclick="this.parentElement.remove(); syncFormToJson();" style="margin-top:1.5rem; width:100%; border-color: rgba(255, 107, 107, 0.3);">Remove Section</button>`;
    list.appendChild(div);
    if (!data) syncFormToJson();
}

function addNestedInput(btn, className, placeholder) {
    const list = btn.parentElement.querySelector('div');
    const existingCount = list.children.length;
    const div = document.createElement('div');
    div.style.display = 'flex';
    div.style.alignItems = 'center';
    div.style.gap = '8px';
    div.style.marginBottom = '5px';
    
    div.innerHTML = `
        <span style="font-size:0.75rem; color:var(--text-secondary); width:15px">${existingCount + 1}.</span>
        <input type="text" class="input-field ${className}" placeholder="${placeholder}">
    `;
    list.appendChild(div);
    syncFormToJson();
}
// Version 1.2
