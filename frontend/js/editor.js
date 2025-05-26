import { API_BASE, AppState } from './state.js';  // Assumes centralized state.js

// Initialize editor with an options object { onAutoSave }
function initializeEditor({ onAutoSave }) {
    const editor = document.getElementById('note-content');
    const titleInput = document.getElementById('note-title');
    
    if (!editor || !titleInput) {
        console.error('Editor elements not found');
        return;
    }

    let saveTimeout;

    // Auto-save after 2 seconds of inactivity
    const autoSave = () => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            if (AppState.currentNote && onAutoSave) {
                onAutoSave();
            }
        }, 2000);
    };

    // Bind event listeners
    editor.addEventListener('input', (event) => {
        isEditing = true;
        autoSave();
        handleLinkDetection(event);
    });

    editor.addEventListener('keydown', handleEditorKeydown);
    titleInput.addEventListener('input', autoSave);
}

// isEditing flag outside function scope
let isEditing = false;

function handleEditorKeydown(event) {
    // Handle Tab key for indentation
    if (event.key === 'Tab') {
        event.preventDefault();
        const editor = event.target;
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        editor.value = editor.value.substring(0, start) + '\t' + editor.value.substring(end);
        editor.selectionStart = editor.selectionEnd = start + 1;
    }

    // Ctrl+S for manual save
    if (event.ctrlKey && (event.key === 's' || event.key === 'S')) {
        event.preventDefault();
        if (typeof window.saveCurrentNote === 'function') {
            window.saveCurrentNote();
        } else {
            console.warn('saveCurrentNote() not defined');
        }
    }

    // Ctrl+N for new note
    if (event.ctrlKey && (event.key === 'n' || event.key === 'N')) {
        event.preventDefault();
        if (typeof window.createNewNote === 'function') {
            window.createNewNote();
        } else {
            console.warn('createNewNote() not defined');
        }
    }
}

function handleLinkDetection(event) {
    const content = event.target.value;
    const cursorPosition = event.target.selectionStart;

    const linkRegex = /\[\[([^\]]+)\]\]/g;
    let match;

    while ((match = linkRegex.exec(content)) !== null) {
        const linkText = match[1];
        const linkStart = match.index;
        const linkEnd = linkStart + match[0].length;

        if (cursorPosition >= linkStart && cursorPosition <= linkEnd) {
            showLinkSuggestions(linkText, linkStart, linkEnd);
            return;
        }
    }

    hideLinkSuggestions();
}

async function showLinkSuggestions(linkText, start, end) {
    try {
        const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(linkText)}&limit=5`);
        const body = await response.json();

        let suggestions = Array.isArray(body)
            ? body
            : Array.isArray(body.suggestions)
                ? body.suggestions
                : [];

        if (suggestions.length === 0) {
            console.warn('No suggestions array found in response:', body);
        }

        displayLinkSuggestions(suggestions, linkText, start, end);
    } catch (error) {
        console.error('Failed to fetch link suggestions:', error);
    }
}

function displayLinkSuggestions(suggestions, linkText, start, end) {
    let dropdown = document.getElementById('link-suggestions');

    if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.id = 'link-suggestions';
        dropdown.className = 'link-suggestions-dropdown';
        document.body.appendChild(dropdown);
    }

    const editor = document.getElementById('note-content');
    const rect = editor.getBoundingClientRect();
    dropdown.style.left = rect.left + 'px';
    dropdown.style.top = (rect.top + 100) + 'px'; // Approximate position

    dropdown.innerHTML = '';

    if (!Array.isArray(suggestions) || suggestions.length === 0) {
        const noResults = document.createElement('div');
        noResults.className = 'suggestion-item no-results';
        noResults.textContent = `No notes found. Press Enter to create "${linkText}"`;
        dropdown.appendChild(noResults);
    } else {
        suggestions.forEach(note => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.innerHTML = `
                <div class="suggestion-title">${note.title}</div>
                <div class="suggestion-preview">${(note.content || '').substring(0, 100)}...</div>
            `;
            item.addEventListener('click', () => {
                selectSuggestion(note.title, start, end);
            });
            dropdown.appendChild(item);
        });
    }

    dropdown.style.display = 'block';
}

// Stub: you need to implement or import selectSuggestion and hideLinkSuggestions
function selectSuggestion(title, start, end) {
    const editor = document.getElementById('note-content');
    const content = editor.value;
    // Replace [[...]] with selected title
    editor.value = content.substring(0, start) + title + content.substring(end);
    editor.focus();
    hideLinkSuggestions();
}

function hideLinkSuggestions() {
    const dropdown = document.getElementById('link-suggestions');
    if (dropdown) {
        dropdown.style.display = 'none';
    }
}

export { initializeEditor, handleEditorKeydown, handleLinkDetection, displayLinkSuggestions };

