-- Revert new_project:alter_portfolio from pg

BEGIN;

ALTER TABLE IF EXISTS profile DROP COLUMN skill_title_design;
ALTER TABLE IF EXISTS profile DROP COLUMN skill_title_video;
ALTER TABLE IF EXISTS profile DROP COLUMN skill_title_soft;

COMMIT;
