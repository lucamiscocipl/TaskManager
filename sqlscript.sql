-- Task Manager API: PostgreSQL schema and repository-query reference
--
-- Parameters such as :project_id are named application bind parameters.
-- Replace them with values in a SQL client, or pass them through SQLAlchemy.
-- SQLAlchemy may satisfy some primary-key lookups from its session cache without
-- issuing SQL; the SELECT statements below show the database form when queried.


-- ==========================================================================
-- SCHEMA
-- ==========================================================================

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(25) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS project_members (
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (project_id, user_id)
);

CREATE TABLE IF NOT EXISTS task_images (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    uploader_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(255) NOT NULL,
    size_bytes BIGINT NOT NULL,
    image_data BYTEA NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_task_images_task_id
    ON task_images (task_id);


-- ==========================================================================
-- USER REPOSITORY
-- ==========================================================================

-- UserRepository.save()
INSERT INTO users (
    username,
    hashed_password
)
VALUES (
    :username,
    :hashed_password
)
RETURNING id, username, hashed_password;

-- UserRepository.get_by_username()
SELECT
    id,
    username,
    hashed_password
FROM users
WHERE username = :username;

-- UserRepository.get_by_id()
SELECT
    id,
    username,
    hashed_password
FROM users
WHERE id = :user_id;


-- ==========================================================================
-- PROJECT REPOSITORY
-- ==========================================================================

-- ProjectRepository.save()
INSERT INTO projects (
    title,
    description,
    owner_id
)
VALUES (
    :title,
    :description,
    :owner_id
)
RETURNING id, title, description, owner_id;

-- ProjectRepository.get_all()
SELECT
    id,
    title,
    description,
    owner_id
FROM projects
ORDER BY id;

-- ProjectRepository.get_by_id()
SELECT
    id,
    title,
    description,
    owner_id
FROM projects
WHERE id = :project_id;

-- Project creation and owner membership as one conceptual transaction.
-- The current repositories commit each save separately; a future unit-of-work
-- can use this transaction to make both writes atomic.
BEGIN;

WITH new_project AS (
    INSERT INTO projects (
        title,
        description,
        owner_id
    )
    VALUES (
        :title,
        :description,
        :owner_id
    )
    RETURNING id
)
INSERT INTO project_members (
    project_id,
    user_id
)
SELECT
    id,
    :owner_id
FROM new_project;

COMMIT;


-- ==========================================================================
-- PROJECT MEMBER REPOSITORY
-- ==========================================================================

-- ProjectMemberRepository.save()
INSERT INTO project_members (
    project_id,
    user_id
)
VALUES (
    :project_id,
    :user_id
)
RETURNING project_id, user_id, joined_at;

-- ProjectMemberRepository.get()
-- This is also the membership authorization check used by task images.
SELECT
    project_id,
    user_id,
    joined_at
FROM project_members
WHERE project_id = :project_id
  AND user_id = :user_id;

-- A minimal membership existence check when metadata is not required.
SELECT EXISTS (
    SELECT 1
    FROM project_members
    WHERE project_id = :project_id
      AND user_id = :user_id
) AS is_project_member;

-- ProjectMemberRepository.get_by_project()
SELECT
    project_id,
    user_id,
    joined_at
FROM project_members
WHERE project_id = :project_id
ORDER BY joined_at, user_id;

-- ProjectMemberRepository.delete()
DELETE FROM project_members
WHERE project_id = :project_id
  AND user_id = :user_id;


-- ==========================================================================
-- TASK REPOSITORY
-- ==========================================================================

-- TaskRepository.save() for a new task.
INSERT INTO tasks (
    title,
    description,
    status,
    project_id,
    user_id
)
VALUES (
    :title,
    :description,
    :status,
    :project_id,
    :user_id
)
RETURNING id, title, description, status, project_id, user_id;

-- TaskRepository.get_by_project()
SELECT
    id,
    title,
    description,
    status,
    project_id,
    user_id
FROM tasks
WHERE project_id = :project_id
ORDER BY id;

-- TaskRepository.get_one_by_project()
-- Requiring both IDs prevents accessing a task through the wrong project URL.
SELECT
    id,
    title,
    description,
    status,
    project_id,
    user_id
FROM tasks
WHERE id = :task_id
  AND project_id = :project_id;

-- TaskRepository.get_by_user()
SELECT
    id,
    title,
    description,
    status,
    project_id,
    user_id
FROM tasks
WHERE user_id = :user_id
ORDER BY id;

-- SQLAlchemy emits an UPDATE for dirty fields when save() receives an
-- existing task. This represents assigning a task to a user.
UPDATE tasks
SET user_id = :user_id
WHERE id = :task_id
  AND project_id = :project_id
RETURNING id, title, description, status, project_id, user_id;


-- ==========================================================================
-- TASK IMAGE REPOSITORY
-- ==========================================================================

-- TaskImageRepository.save()
-- Metadata and BYTEA content are inserted together in one row.
INSERT INTO task_images (
    task_id,
    uploader_id,
    original_filename,
    content_type,
    size_bytes,
    image_data
)
VALUES (
    :task_id,
    :uploader_id,
    :original_filename,
    :content_type,
    :size_bytes,
    :image_data
)
RETURNING
    id,
    task_id,
    uploader_id,
    original_filename,
    content_type,
    size_bytes,
    created_at;

-- TaskImageRepository.get_by_task()
-- METADATA ONLY: image_data is deliberately omitted. This is the SQL
-- equivalent of options(defer(TaskImage.image_data)).
SELECT
    id,
    task_id,
    uploader_id,
    original_filename,
    content_type,
    size_bytes,
    created_at
FROM task_images
WHERE task_id = :task_id
ORDER BY created_at, id;

-- TaskImageRepository.get_one()
-- COMPLETE ROW: the service uses this when it needs image content or when it
-- checks ownership before deletion.
SELECT
    id,
    task_id,
    uploader_id,
    original_filename,
    content_type,
    size_bytes,
    image_data,
    created_at
FROM task_images
WHERE id = :image_id
  AND task_id = :task_id;

-- Optimized content-only form for the image-content endpoint.
-- The current repository loads the complete row; this narrower query can be
-- introduced later if only bytes and MIME type are needed.
SELECT
    image_data,
    content_type
FROM task_images
WHERE id = :image_id
  AND task_id = :task_id;

-- TaskImageRepository.delete()
DELETE FROM task_images
WHERE id = :image_id
  AND task_id = :task_id;


-- ==========================================================================
-- TASK IMAGE SERVICE ACCESS SEQUENCE
-- ==========================================================================

-- 1. Confirm that the project exists and obtain its owner.
SELECT
    id,
    owner_id
FROM projects
WHERE id = :project_id;

-- 2. Confirm that the authenticated user is a project member.
SELECT
    project_id,
    user_id,
    joined_at
FROM project_members
WHERE project_id = :project_id
  AND user_id = :current_user_id;

-- 3. Confirm that the task belongs to the project.
SELECT
    id,
    project_id
FROM tasks
WHERE id = :task_id
  AND project_id = :project_id;

-- 4. Retrieve image ownership before deletion.
SELECT
    id,
    uploader_id
FROM task_images
WHERE id = :image_id
  AND task_id = :task_id;

-- Application authorization rule after the preceding SELECT statements:
-- deletion is allowed when uploader_id = :current_user_id
-- OR project.owner_id = :current_user_id.


-- ==========================================================================
-- CASCADE EFFECTS
-- ==========================================================================

-- Because task_images.task_id uses ON DELETE CASCADE, deleting a task also
-- removes its image metadata and BYTEA content.
DELETE FROM tasks
WHERE id = :task_id;

-- Because task_images.uploader_id uses ON DELETE CASCADE, deleting a user also
-- removes images uploaded by that user.
DELETE FROM users
WHERE id = :user_id;
