## Purpose

Lets a user create, view, edit, and delete personal AI learning notes, with each note organized under one of 5 fixed chapters and persisted in a local SQLite database.

## ADDED Requirements

### Requirement: Fixed chapter set
The system SHALL provide exactly 5 fixed chapters for organizing notes: 应用层 (Application Layer), 连接层 (Connection Layer), 交互层 (Interaction Layer), 记忆层 (Memory Layer), and 基础层 (Foundation Layer). Users SHALL NOT be able to create, rename, or delete chapters.

#### Scenario: Chapters are available on startup
- **WHEN** the application starts
- **THEN** all 5 fixed chapters are available for browsing and note creation

### Requirement: Create note
The system SHALL allow a user to create a new note by specifying a title, body content, and a chapter (one of the 5 fixed chapters). The note SHALL be persisted to the SQLite database with a creation timestamp.

#### Scenario: Successful note creation
- **WHEN** a user submits a new note with a non-empty title, body, and a selected chapter
- **THEN** the system saves the note to the database and it appears in that chapter's note list

#### Scenario: Missing required field
- **WHEN** a user attempts to submit a new note with an empty title or empty body
- **THEN** the system rejects the submission and shows a validation message, and no note is created

### Requirement: View notes by chapter
The system SHALL allow a user to view the list of notes belonging to a selected chapter, and to view the full content of an individual note.

#### Scenario: List notes in a chapter
- **WHEN** a user selects a chapter
- **THEN** the system displays all notes belonging to that chapter, ordered by most recently updated first

#### Scenario: Empty chapter
- **WHEN** a user selects a chapter that has no notes
- **THEN** the system displays an empty state indicating there are no notes yet

### Requirement: Update note
The system SHALL allow a user to edit the title, body, and chapter of an existing note. The system SHALL update the note's last-modified timestamp on save.

#### Scenario: Successful update
- **WHEN** a user edits an existing note's title or body and saves
- **THEN** the system persists the changes and the updated content is reflected immediately in the note view

#### Scenario: Move note to a different chapter
- **WHEN** a user changes a note's chapter and saves
- **THEN** the note is removed from its original chapter's list and appears in the newly selected chapter's list

### Requirement: Delete note
The system SHALL allow a user to permanently delete an existing note after explicit confirmation.

#### Scenario: Successful deletion
- **WHEN** a user confirms deletion of a note
- **THEN** the system removes the note from the database and it no longer appears in any chapter's note list

#### Scenario: Cancel deletion
- **WHEN** a user is prompted to confirm deletion and cancels
- **THEN** the note is not deleted and remains unchanged

### Requirement: Persistent storage
The system SHALL persist all notes in a local SQLite database file so that notes remain available across application restarts.

#### Scenario: Notes survive restart
- **WHEN** the application is stopped and restarted
- **THEN** all previously created notes are still present with their original content and chapter assignment
