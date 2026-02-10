// Skills tag input component
function initSkillsTagInput() {
    const container = document.getElementById('skills-container');
    if (!container) return;

    const input = document.getElementById('skill-input');
    const tagsDisplay = document.getElementById('skills-tags');
    const hiddenInput = document.getElementById('skills-hidden');

    let skills = hiddenInput.value ? hiddenInput.value.split(',').filter(s => s.trim()) : [];

    function renderTags() {
        tagsDisplay.innerHTML = '';
        skills.forEach((skill, index) => {
            const tag = document.createElement('span');
            tag.className = 'pill pill-yellow';
            tag.style.cssText = 'display: inline-flex; align-items: center; gap: 8px; margin: 4px; padding: 6px 12px;';
            tag.innerHTML = `
                ${skill}
                <button type="button" class="remove-skill" data-index="${index}" style="background: none; border: none; cursor: pointer; font-size: 16px; padding: 0; color: inherit;">&times;</button>
            `;
            tagsDisplay.appendChild(tag);
        });

        // Update hidden input
        hiddenInput.value = skills.join(',');

        // Attach remove listeners
        document.querySelectorAll('.remove-skill').forEach(btn => {
            btn.addEventListener('click', function () {
                const index = parseInt(this.dataset.index);
                skills.splice(index, 1);
                renderTags();
            });
        });
    }

    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            const skill = this.value.trim();
            if (skill && !skills.includes(skill)) {
                skills.push(skill);
                renderTags();
                this.value = '';
            }
        }
    });

    renderTags();
}

// Social links dynamic add/remove
function initSocialLinks() {
    const container = document.getElementById('social-links-container');
    if (!container) return;

    const addBtn = document.getElementById('add-social-link');
    const linksWrapper = document.getElementById('social-links-wrapper');

    let linkCount = linksWrapper.querySelectorAll('.social-link-item').length;

    addBtn.addEventListener('click', function () {
        linkCount++;
        const linkItem = document.createElement('div');
        linkItem.className = 'social-link-item';
        linkItem.style.cssText = 'display: flex; gap: 12px; margin-bottom: 12px;';
        linkItem.innerHTML = `
            <select class="form-control" name="social_platform_${linkCount}" style="flex: 0 0 150px;">
                <option value="">Select Platform</option>
                <option value="linkedin">LinkedIn</option>
                <option value="github">GitHub</option>
                <option value="twitter">Twitter</option>
                <option value="instagram">Instagram</option>
                <option value="facebook">Facebook</option>
                <option value="youtube">YouTube</option>
                <option value="website">Website</option>
                <option value="other">Other</option>
            </select>
            <input type="url" class="form-control" name="social_url_${linkCount}" placeholder="https://..." style="flex: 1;">
            <button type="button" class="btn btn-outline btn-small remove-social-link" style="flex: 0 0 auto;">&times;</button>
        `;
        linksWrapper.appendChild(linkItem);

        // Attach remove listener
        linkItem.querySelector('.remove-social-link').addEventListener('click', function () {
            linkItem.remove();
        });
    });

    // Attach remove listeners to existing links
    document.querySelectorAll('.remove-social-link').forEach(btn => {
        btn.addEventListener('click', function () {
            this.closest('.social-link-item').remove();
        });
    });
}

// Autosave functionality with debounce
let autosaveTimeout;
function autosave(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    const inputs = form.querySelectorAll('input[type="text"], textarea');
    const indicator = document.getElementById('autosave-indicator');

    inputs.forEach(input => {
        input.addEventListener('input', function () {
            clearTimeout(autosaveTimeout);

            if (indicator) {
                indicator.textContent = 'Saving...';
                indicator.style.color = '#999';
            }

            autosaveTimeout = setTimeout(() => {
                // Perform AJAX save
                const formData = new FormData(form);
                fetch(form.action, {
                    method: 'POST',
                    body: formData
                })
                    .then(res => res.json())
                    .then(data => {
                        if (indicator) {
                            indicator.textContent = 'Saved ✓';
                            indicator.style.color = 'green';
                            setTimeout(() => {
                                indicator.textContent = '';
                            }, 2000);
                        }
                    })
                    .catch(err => {
                        if (indicator) {
                            indicator.textContent = 'Error saving';
                            indicator.style.color = 'red';
                        }
                    });
            }, 2000);
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    initSkillsTagInput();
    initSocialLinks();
});
