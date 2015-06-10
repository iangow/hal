WITH l AS (select folder from mirror_filing),
     r AS (
     SELECT regexp_replace(
                file_name,
                E'^edgar/data/(\\d+)/(\\d{10})-(\\d{2})-(\\d{6})\\.txt$',
                E'\\1/\\2\\3\\4'
            ) AS folder
            FROM director.equilar_proxies
            GROUP BY folder
     ),
     new_folders AS (SELECT r.folder FROM l RIGHT JOIN r ON l.folder = r.folder WHERE l.folder IS NULL AND r.folder <> '')
INSERT INTO mirror_filing SELECT folder FROM new_folders;
