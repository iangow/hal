WITH directors AS (
    SELECT director.equilar_id(director_id) AS equilar_id, fy_end, director, term_end_date
    FROM director)
SELECT *,
    'http://www.sec.gov/Archives/' || regexp_replace(file_name, 
                   E'(\\d{10})-(\\d{2})-(\\d{6})\\.txt', 
                   E'\\1\\2\\3') AS url
FROM directors 
INNER JOIN equilar_proxies
USING (equilar_id, fy_end)
