USE krushi_samruddhi_odisha;

SET NAMES utf8mb4;

START TRANSACTION;

-- Existing verified Odia names
UPDATE gram_panchayats
SET gp_name_or = 'ରସୁଲପୁର'
WHERE gp_id = 17;

UPDATE gram_panchayats
SET gp_name_or = 'ନରସିଂହପୁର'
WHERE gp_id = 18;

UPDATE gram_panchayats
SET gp_name_or = 'ବରାବାଟି'
WHERE gp_id = 25;

-- Verified Odia names
UPDATE gram_panchayats
SET gp_name_or = 'ଅଟଳପୁର'
WHERE gp_id = 3357;

UPDATE gram_panchayats
SET gp_name_or = 'ବଡକଇଁଚି'
WHERE gp_id = 3358;

UPDATE gram_panchayats
SET gp_name_or = 'ବ୍ରହ୍ମବରଦା'
WHERE gp_id = 3363;

UPDATE gram_panchayats
SET gp_name_or = 'ଗଙ୍ଗାଧରପୁର'
WHERE gp_id = 3365;

UPDATE gram_panchayats
SET gp_name_or = 'ମହେଶ୍ୱରପୁର'
WHERE gp_id = 3371;

UPDATE gram_panchayats
SET gp_name_or = 'ମଙ୍ଗରାଜପୁର'
WHERE gp_id = 3372;

COMMIT;