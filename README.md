# FocusNest

FocusNest is a modern, web-based note-taking and knowledge management system designed to help users not just store, but connect, resurface, and act on their ideas. It combines a powerful FastAPI backend, a responsive and PWA-enabled frontend, and advanced features for deep thinkers, creatives, and professionals.

## Features

### Core Functionality
- Note Creation & Editing: Quickly create, edit, and delete notes with a clean, distraction-free editor.
- Bidirectional Linking: Use `[[Note Title]]` syntax to create and manage links between notes, building a network of ideas.
- Graph Visualization: Interactive, dynamic graph view to visualize notes and their relationships.
- Daily Suggestions & Random Discovery: Smart resurfacing algorithms suggest relevant or forgotten notes to keep your ideas fresh.
- Full-Text Search: Fast, case-insensitive search across all notes by title or content.
- Actionable UI: Highlight, pin, and resurface notes to encourage action, not just organization.

### Modern UI/UX
- Dark Mode: Toggle between light and dark themes for comfortable viewing.
- Responsive Design: Fully mobile-friendly layout with touch-friendly controls.
- Collapsible & Grouped Notes: Notes are grouped by date (Today, This Week, Earlier) and can be collapsed for clarity. Pagination keeps lists manageable.
- Preview & Word Count: Live markdown preview and word count in the editor.

### Progressive Web App (PWA)
- Installable: Add FocusNest to your home screen
- Offline Support: Core UI and static assets work offline; dynamic features require connectivity.
- Manifest & Icons: Custom app icon and theme color for a native feel.

### Backend & Data
- FastAPI Backend: Robust REST API for notes, search, graph data, and resurfacing.
- SQLite Database: Lightweight, portable storage for notes and metadata.
- Resurfacing Algorithms: Suggest notes based on recency, connections, and engagement.