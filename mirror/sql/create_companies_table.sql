DROP TABLE IF EXISTS companies;

SELECT DISTINCT regexp_replace(director_id, '\..*$', '') as equilar_id, company
    INTO companies FROM director;
