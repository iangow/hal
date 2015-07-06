DROP TABLE IF EXISTS crosswalk;

WITH x AS
( 
       SELECT regexp_replace(file_name, e'^edgar/data/(\\d+)/(\\d{10})-(\\d{2})-(\\d{6})\\.txt$', e'\\1/\\2\\3\\4') AS folder, 
              equilar_id, 
              fy_end 
       FROM   equilar_proxies ) 
SELECT DISTINCT folder, 
       director_id, 
       director 
INTO   crosswalk 
FROM   director 
JOIN   x 
ON     regexp_replace(director_id, '\..*$', '')::integer=equilar_id 
AND    director.fy_end=x.fy_end 
AND    folder <> '';
