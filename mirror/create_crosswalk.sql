WITH x AS
( 
       SELECT regexp_replace(file_name, e'^edgar/data/(\\d+)/(\\d{10})-(\\d{2})-(\\d{6})\\.txt$', e'\\1/\\2\\3\\4') AS folder, 
              equilar_id, 
              fy_end 
       FROM   director.equilar_proxies ) 
SELECT DISTINCT folder, 
       director_id, 
       director 
INTO   crosswalk 
FROM   director.director 
JOIN   x 
ON     director.equilar_id(director_id)=equilar_id 
AND    director.director.fy_end=x.fy_end 
AND    folder <> '';
