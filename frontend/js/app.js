import { initializeEditor } from './editor.js';
import { toggleSearch, closeSearch, performSearch } from './search.js';
import { toggleGraph, closeGraph } from './graph.js';
import { AppState, API_BASE } from './state.js';

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    await initializeApp();
    setupEventListeners();
    initializeEditor({ onAutoSave: saveCurrentNote });
    await loadRecentNotes();
    await loadDailySuggestions();
});

async function initializeApp() {
    console.log('🧠 FocusNest - Initializing...');
    try {
        const response = await fetch('/health');
        if (response.ok) {
            console.log('✅ Backend connected successfully');
        }
    } catch (error) {
        console.error('❌ Backend connection failed:', error);
        showNotification('Backend connection failed', 'error');
    }
}

function setupEventListeners() {
    document.getElementById('new-note-btn').addEventListener('click', createNewNote);
    document.getElementById('search-toggle').addEventListener('click', toggleSearch);
    document.getElementById('graph-toggle').addEventListener('click', toggleGraph);
    document.getElementById('save-note').addEventListener('click', saveCurrentNote);
    document.getElementById('delete-note').addEventListener('click', deleteCurrentNote);
    document.getElementById('preview-toggle').addEventListener('click', togglePreview);
    document.getElementById('close-search').addEventListener('click', closeSearch);
    document.getElementById('search-input').addEventListener('input', debounce(performSearch, 300));
    document.getElementById('close-graph').addEventListener('click', closeGraph);
    document.getElementById('refresh-suggestions').addEventListener('click', loadDailySuggestions);
    document.getElementById('random-discovery').addEventListener('click', loadRandomNote);
    document.getElementById('dark-mode-toggle').addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const btn = document.getElementById('dark-mode-toggle');
        if (document.body.classList.contains('dark-mode')) {
            btn.textContent = '☀️ Light Mode';
        } else {
            btn.textContent = '🌙 Dark Mode';
        }
    });
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

// Notes
async function loadRecentNotes() {
    try {
        const response = await fetch(`${API_BASE}/notes/`);
        const notes = await response.json();
        AppState.notes = notes;
        renderRecentNotes(notes);
        // Also populate all notes section if it exists
        const allNotesContainer = document.getElementById('all-notes');
        if (allNotesContainer) {
            renderAllNotes(notes);
        }
    } catch (error) {
        console.error('Failed to load notes:', error);
        showNotification('Failed to load notes', 'error');
    }
}

function renderRecentNotes(notes) {
    const container = document.getElementById('recent-notes');
    container.innerHTML = '';
    notes.slice(0, 10).forEach(note => {
        const noteElement = createNoteListItem(note);
        container.appendChild(noteElement);
    });
}

function groupNotesByDate(notes) {
    const groups = { Today: [], 'This Week': [], Earlier: [] };
    const now = new Date();
    notes.forEach(note => {
        const updated = new Date(note.updated_at);
        const diffDays = (now - updated) / (1000 * 60 * 60 * 24);
        if (diffDays < 1) {
            groups.Today.push(note);
        } else if (diffDays < 7) {
            groups['This Week'].push(note);
        } else {
            groups.Earlier.push(note);
        }
    });
    return groups;
}

function renderAllNotes(notes) {
    const container = document.getElementById('all-notes');
    if (!container) return;
    container.innerHTML = '';
    const groups = groupNotesByDate(notes);
    Object.entries(groups).forEach(([group, groupNotes]) => {
        if (groupNotes.length === 0) return;
        // Collapsible group header
        const groupHeader = document.createElement('div');
        groupHeader.className = 'note-group-header';
        groupHeader.innerHTML = `<span>${group} (${groupNotes.length})</span> <button class="toggle-group">▼</button>`;
        container.appendChild(groupHeader);
        // Group notes container
        const groupContainer = document.createElement('div');
        groupContainer.className = 'note-group-container';
        groupContainer.style.display = 'block';
        // Pagination: show only first 10, add Load More if needed
        let shown = 10;
        function renderGroupNotes() {
            groupContainer.innerHTML = '';
            groupNotes.slice(0, shown).forEach(note => {
                const noteElement = createNoteListItem(note);
                groupContainer.appendChild(noteElement);
            });
            if (shown < groupNotes.length) {
                const loadMore = document.createElement('button');
                loadMore.className = 'btn btn-small load-more';
                loadMore.textContent = 'Load More';
                loadMore.onclick = () => {
                    shown += 10;
                    renderGroupNotes();
                };
                groupContainer.appendChild(loadMore);
            }
        }
        renderGroupNotes();
        container.appendChild(groupContainer);
        // Collapsing logic
        groupHeader.querySelector('.toggle-group').onclick = () => {
            if (groupContainer.style.display === 'none') {
                groupContainer.style.display = 'block';
                groupHeader.querySelector('.toggle-group').textContent = '▼';
            } else {
                groupContainer.style.display = 'none';
                groupHeader.querySelector('.toggle-group').textContent = '►';
            }
        };
    });
}

function createNoteListItem(note) {
    const element = document.createElement('div');
    element.className = 'note-item';
    element.innerHTML = `
        <h4>${escapeHtml(note.title)}</h4>
        <p class="note-preview">${escapeHtml(note.content.substring(0, 100))}${note.content.length > 100 ? '...' : ''}</p>
    `;
    element.addEventListener('click', () => loadNote(note.id));
    // Highlight selected note
    if (AppState.currentNote && AppState.currentNote.id === note.id) {
        element.classList.add('selected');
    }
    return element;
}

async function loadNote(noteId) {
    try {
        const response = await fetch(`${API_BASE}/notes/${noteId}`);
        const note = await response.json();
        AppState.currentNote = note;
        document.getElementById('note-title').value = note.title;
        document.getElementById('note-content').value = note.content;
        document.getElementById('delete-note').style.display = 'block';
        updateWordCount();
        updatePreview();
        showNotification(`Loaded: ${note.title}`, 'success');
    } catch (error) {
        console.error('Failed to load note:', error);
        showNotification('Failed to load note', 'error');
    }
}

function createNewNote() {
    AppState.currentNote = null;
    document.getElementById('note-title').value = '';
    document.getElementById('note-content').value = '';
    document.getElementById('delete-note').style.display = 'none';
    document.getElementById('note-title').focus();
    updateWordCount();
    updatePreview();
}

async function saveCurrentNote() {
    const title = document.getElementById('note-title').value.trim();
    const content = document.getElementById('note-content').value;

    if (!title) {
        showNotification('Please enter a note title', 'error');
        return;
    }

    try {
        const noteData = { title, content };
        let response;

        if (AppState.currentNote) {
            response = await fetch(`${API_BASE}/notes/${AppState.currentNote.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(noteData)
            });
        } else {
            response = await fetch(`${API_BASE}/notes/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(noteData)
            });
        }

        if (response.ok) {
            const savedNote = await response.json();
            AppState.currentNote = savedNote;
            document.getElementById('delete-note').style.display = 'block';
            await loadRecentNotes();
            showNotification('Note saved successfully', 'success');
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Failed to save note', 'error');
        }
    } catch (error) {
        console.error('Failed to save note:', error);
        showNotification('Failed to save note', 'error');
    }
}

async function deleteCurrentNote() {
    if (!AppState.currentNote) return;
    if (!confirm(`Are you sure you want to delete "${AppState.currentNote.title}"?`)) return;

    try {
        const response = await fetch(`${API_BASE}/notes/${AppState.currentNote.id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            createNewNote();
            await loadRecentNotes();
            showNotification('Note deleted successfully', 'success');
        } else {
            showNotification('Failed to delete note', 'error');
        }
    } catch (error) {
        console.error('Failed to delete note:', error);
        showNotification('Failed to delete note', 'error');
    }
}

// Preview
function togglePreview() {
    AppState.isPreviewMode = !AppState.isPreviewMode;
    const content = document.getElementById('note-content');
    const preview = document.getElementById('note-preview');
    const button = document.getElementById('preview-toggle');

    if (AppState.isPreviewMode) {
        content.style.display = 'none';
        preview.style.display = 'block';
        button.textContent = '✏️ Edit';
        updatePreview();
    } else {
        content.style.display = 'block';
        preview.style.display = 'none';
        button.textContent = '👁️ Preview';
    }
}

async function updatePreview() {
    if (!AppState.isPreviewMode) return;
    const content = document.getElementById('note-content').value;
    const preview = document.getElementById('note-preview');

    let html = marked.parse(content);

    if (AppState.currentNote) {
        try {
            const response = await fetch(`${API_BASE}/notes/${AppState.currentNote.id}/render`);
            const result = await response.json();
            html = marked.parse(result.content);
        } catch (error) {
            console.warn('Failed to render links:', error);
        }
    }

    preview.innerHTML = html;

    preview.querySelectorAll('.note-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const noteId = parseInt(link.dataset.noteId);
            loadNote(noteId);
        });
    });
}

// Word count
function updateWordCount() {
    const content = document.getElementById('note-content').value;
    const words = content.trim() ? content.trim().split(/\s+/).length : 0;
    document.getElementById('word-count').textContent = `${words} words`;
}

// Daily suggestions
async function loadDailySuggestions() {
    try {
        const response = await fetch(`${API_BASE}/search/resurface/daily`);
        const result = await response.json();
        renderSuggestions(result.notes);
    } catch (error) {
        console.error('Failed to load suggestions:', error);
    }
}

function renderSuggestions(suggestions) {
    const container = document.getElementById('daily-suggestions');
    container.innerHTML = '';
    suggestions.forEach(note => {
        const element = document.createElement('div');
        element.className = 'suggestion-item';
        element.innerHTML = `
            <strong>${escapeHtml(note.title)}</strong>
            <p>${escapeHtml(note.content.substring(0, 60))}...</p>
        `;
        element.addEventListener('click', () => loadNote(note.id));
        container.appendChild(element);
    });
}

// Random discovery
async function loadRandomNote() {
    try {
        const response = await fetch(`${API_BASE}/search/resurface/random`);
        const result = await response.json();
        if (result.note) {
            renderRandomNote(result.note);
        } else {
            document.getElementById('random-note').innerHTML = '<p>No notes found for discovery</p>';
        }
    } catch (error) {
        console.error('Failed to load random note:', error);
    }
}

function renderRandomNote(note) {
    const container = document.getElementById('random-note');
    container.innerHTML = `
        <div class="suggestion-item">
            <strong>${escapeHtml(note.title)}</strong>
            <p>${escapeHtml(note.content.substring(0, 80))}...</p>
        </div>
    `;
    container.querySelector('.suggestion-item').addEventListener('click', () => loadNote(note.id));
}

// Shortcuts
function handleKeyboardShortcuts(e) {
    if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
            case 's':
                e.preventDefault();
                saveCurrentNote();
                break;
            case 'n':
                e.preventDefault();
                createNewNote();
                break;
            case 'f':
                e.preventDefault();
                toggleSearch();
                break;
            case 'p':
                e.preventDefault();
                togglePreview();
                break;
        }
    }

    if (e.key === 'Escape') {
        closeSearch();
        closeGraph();
    }
}

// Utils
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#6c5ce7'};
        color: white;
        border-radius: 4px;
        z-index: 1001;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    notification.textContent = message;

    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}


export { loadNote };
