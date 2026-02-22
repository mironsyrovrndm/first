-- Deploy new_project:admin_user to pg

BEGIN;

INSERT INTO users (username, password_hash)
    VALUES ('stas', 'scrypt:32768:8:1$X34e4ternrC69uGe$02d8687d21fec23c09b8df579d99426a4a3d74e0bb53ec741e36cdf3cc7d612663d1a2ef044f895d5006ddfe2edae46783376962857a20e7c968aa6c10402f7a');

COMMIT;
