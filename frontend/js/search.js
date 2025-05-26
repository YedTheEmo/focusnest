import { API_BASE } from './state.js';
import { loadNote } from './app.js'; // If you move `loadNote` to a shared utility, update this path accordingly

let searchTimeout;

function toggleSearch() {
    const overlay = document.getElementById('search-overlay');
    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');

    const isHidden = overlay.style.display === 'none' || getComputedStyle(overlay).display === 'none';

    if (isHidden) {
        overlay.style.display = 'flex';
        input.focus();
        input.value = '';
        results.innerHTML = '';
    } else {
        closeSearch();
    }
}

function closeSearch() {
    document.getElementById('search-overlay').style.display = 'none';
}

async function performSearch() {
    const query = document.getElementById('search-input').value.trim();
    const resultsContainer = document.getElementById('search-results');

    if (query.length < 2) {
        resultsContainer.innerHTML = `
            <div style="padding: 1rem; text-align: center; color: #6c757d;">
                Type at least 2 characters to search...
            </div>`;
        return;
    }

    try {
        resultsContainer.innerHTML = `
            <div style="padding: 1rem; text-align: center;">
                Searching...
            </div>`;

        const response = await fetch(`${API_BASE}/search/?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        renderSearchResults(results.notes);
    } catch (error) {
        console.error('Search failed:', error);
        resultsContainer.innerHTML = `
            <div style="padding: 1rem; text-align: center; color: #dc3545;">
                Search failed. Please try again.
            </div>`;
    }
}

function renderSearchResults(notes) {
    const container = document.getElementById('search-results');

    if (!notes.length) {
        container.innerHTML = `
            <div style="padding: 1rem; text-align: center; color: #6c757d;">
                No notes found.
            </div>`;
        return;
    }

    container.innerHTML = '';
    notes.forEach(note => {
        const element = document.createElement('div');
        element.className = 'search-result-item';
        element.innerHTML = `
            <div class="search-result-title">${escapeHtml(note.title)}</div>
            <div class="search-result-content">${escapeHtml(note.content.substring(0, 120))}...</div>
        `;

        element.addEventListener('click', () => {
            loadNote(note.id);
            closeSearch();
        });

        container.appendChild(element);
    });
}

// Utility: Escape HTML to prevent injection
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close overlay when clicking outside the modal box
document.getElementById('search-overlay').addEventListener('click', (e) => {
    if (e.target.id === 'search-overlay') {
        closeSearch();
    }
});

export {
    toggleSearch,
    closeSearch,
    performSearch,
    renderSearchResults
};
