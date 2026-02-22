-- Deploy new_project:alter_portfolio to pg

BEGIN;

ALTER TABLE IF EXISTS profile ADD COLUMN skill_title_design TEXT;
ALTER TABLE IF EXISTS profile ADD COLUMN skill_title_video TEXT;
ALTER TABLE IF EXISTS profile ADD COLUMN skill_title_soft TEXT;

COMMIT;
