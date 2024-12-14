CREATE ROLE username_access;

CREATE POLICY username_policy 
ON ghtorrent_restore_2015.projects
TO username_access
USING (id=4);

ALTER TABLE ghtorrent_restore_2015.projects ENABLE ROW LEVEL SECURITY;

CREATE USER username;
ALTER USER username WITH PASSWORD '123';
GRANT username_access TO username;

GRANT USAGE ON SCHEMA ghtorrent_restore_2015 TO username;
GRANT SELECT ON ALL TABLES IN SCHEMA ghtorrent_restore_2015 TO username;
ALTER DEFAULT PRIVILEGES IN SCHEMA ghtorrent_restore_2015
GRANT SELECT ON TABLES TO username;

