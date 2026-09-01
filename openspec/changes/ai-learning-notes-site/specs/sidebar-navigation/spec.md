## Purpose

Provides a sidebar-based navigation UI so a user can browse the 5 fixed chapters and switch between them to view and manage that chapter's notes.

## ADDED Requirements

### Requirement: Sidebar chapter list
The system SHALL display a sidebar listing all 5 fixed chapters, each identified by its name (e.g., 应用层, 连接层, 交互层, 记忆层, 基础层).

#### Scenario: Sidebar shows all chapters
- **WHEN** the application loads
- **THEN** the sidebar displays all 5 fixed chapters in a consistent, fixed order

### Requirement: Chapter selection updates main content
The system SHALL update the main content area to show the selected chapter's notes when a user clicks a chapter in the sidebar.

#### Scenario: Selecting a chapter
- **WHEN** a user clicks a chapter in the sidebar
- **THEN** the main content area displays that chapter's note list, and the sidebar indicates which chapter is currently selected

### Requirement: Default chapter on load
The system SHALL display a default chapter's notes in the main content area when the application first loads, without requiring the user to make a selection.

#### Scenario: Initial load
- **WHEN** the application is opened for the first time in a session
- **THEN** the first chapter in the sidebar is selected by default and its notes are shown in the main content area
