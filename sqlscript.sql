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



INSERT INTO users (
    username,
    hashed_password
)
VALUES (
    :username,
    :hashed_password
)
RETURNING id, username, hashed_password;

SELECT
    id,
    username,
    hashed_password
FROM users
WHERE username = :username;

SELECT
    id,
    username,
    hashed_password
FROM users
WHERE id = :user_id;



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

SELECT
    id,
    title,
    description,
    owner_id
FROM projects
ORDER BY id;

SELECT
    id,
    title,
    description,
    owner_id
FROM projects
WHERE id = :project_id;

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



INSERT INTO project_members (
    project_id,
    user_id
)
VALUES (
    :project_id,
    :user_id
)
RETURNING project_id, user_id, joined_at;

SELECT
    project_id,
    user_id,
    joined_at
FROM project_members
WHERE project_id = :project_id
  AND user_id = :user_id;

SELECT EXISTS (
    SELECT 1
    FROM project_members
    WHERE project_id = :project_id
      AND user_id = :user_id
) AS is_project_member;

SELECT
    project_id,
    user_id,
    joined_at
FROM project_members
WHERE project_id = :project_id
ORDER BY joined_at, user_id;

DELETE FROM project_members
WHERE project_id = :project_id
  AND user_id = :user_id;



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

UPDATE tasks
SET user_id = :user_id
WHERE id = :task_id
  AND project_id = :project_id
RETURNING id, title, description, status, project_id, user_id;



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

SELECT
    image_data,
    content_type
FROM task_images
WHERE id = :image_id
  AND task_id = :task_id;

DELETE FROM task_images
WHERE id = :image_id
  AND task_id = :task_id;

SELECT
    id,
    owner_id
FROM projects
WHERE id = :project_id;

SELECT
    project_id,
    user_id,
    joined_at
FROM project_members
WHERE project_id = :project_id
  AND user_id = :current_user_id;

SELECT
    id,
    project_id
FROM tasks
WHERE id = :task_id
  AND project_id = :project_id;

SELECT
    id,
    uploader_id
FROM task_images
WHERE id = :image_id
  AND task_id = :task_id;


DELETE FROM tasks
WHERE id = :task_id;


DELETE FROM users
WHERE id = :user_id;
