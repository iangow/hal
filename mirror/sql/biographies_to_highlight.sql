SELECT setseed(1);

WITH t1 AS (
    SELECT DISTINCT a AS d_id
    FROM matched_director_ids
    ),
    t2 AS (
    SELECT *
    FROM t1 JOIN crosswalk
    ON d_id=regexp_replace(director_id, '\..*\.', '.')
    ),
    t3 AS (
    SELECT DISTINCT regexp_replace(uri, 'http://hal.marder.io/highlight/', '') AS folder
    FROM mirror_highlight
    )
    SELECT t2.folder, director_id, director FROM t2 JOIN t3
    ON t2.folder=t3.folder ORDER BY random();
