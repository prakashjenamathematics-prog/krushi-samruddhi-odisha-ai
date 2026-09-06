USE krushi_samruddhi_odisha;

SET NAMES utf8mb4;

START TRANSACTION;

UPDATE gram_panchayats
SET gp_name_or = CASE gp_id

    WHEN 3356 THEN 'ଅର୍ଥଙ୍ଗା'
    WHEN 3359 THEN 'ବାହାଦଳପୁର'
    WHEN 3360 THEN 'ବନ୍ଧାଦିହା'
    WHEN 3361 THEN 'ଭବାନୀପୁର (ଭୁବନ)'
    WHEN 3362 THEN 'ଭୋଟକା'
    WHEN 3364 THEN 'ଗନ୍ଧନ'
    WHEN 3366 THEN 'ଜାବରା'
    WHEN 3367 THEN 'କଳନା'
    WHEN 3368 THEN 'ଖମଣ'
    WHEN 3369 THEN 'ଲକ୍ଷ୍ମୀନଗର'
    WHEN 3370 THEN 'ମୁଗୁପାଳ'
    WHEN 3373 THEN 'ନାଥୁଆବର'
    WHEN 3374 THEN 'ଓଡ଼ିସୋ'
    WHEN 3375 THEN 'ପହଙ୍ଗା'
    WHEN 3376 THEN 'ପ୍ରଥମାଖଣ୍ଡି'
    WHEN 3377 THEN 'ରହମ୍ବା'
    WHEN 3378 THEN 'ରାଜେନ୍ଦ୍ରପୁର'
    WHEN 3379 THEN 'ରାଉତରାପୁର'
    WHEN 3380 THEN 'ସାମନ୍ତରାପୁର'
    WHEN 3381 THEN 'ସିଂହାପୁର'
    WHEN 3382 THEN 'ଶ୍ରୀବନ୍ତପୁର'
    WHEN 3383 THEN 'ଟିକରପଡ଼ା'

    ELSE gp_name_or

END
WHERE gp_id IN (
    3356, 3359, 3360, 3361, 3362, 3364,
    3366, 3367, 3368, 3369, 3370, 3373,
    3374, 3375, 3376, 3377, 3378, 3379,
    3380, 3381, 3382, 3383
);

COMMIT;