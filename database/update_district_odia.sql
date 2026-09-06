USE krushi_samruddhi_odisha;

SET NAMES utf8mb4;

START TRANSACTION;

UPDATE districts
SET district_name_or = CASE district_id
    WHEN 1 THEN 'ଯାଜପୁର'
    WHEN 2 THEN 'ଭଦ୍ରକ'
    WHEN 3 THEN 'ବାଲେଶ୍ୱର'
    WHEN 5 THEN 'ପୁରୀ'
    WHEN 6 THEN 'କଟକ'
    WHEN 7 THEN 'ଅନୁଗୁଳ'
    WHEN 8 THEN 'ବଲାଙ୍ଗୀର'
    WHEN 9 THEN 'ବରଗଡ଼'
    WHEN 10 THEN 'ବୌଦ୍ଧ'
    WHEN 11 THEN 'ଦେବଗଡ଼'
    WHEN 12 THEN 'ଢେଙ୍କାନାଳ'
    WHEN 13 THEN 'ଗଜପତି'
    WHEN 14 THEN 'ଗଞ୍ଜାମ'
    WHEN 15 THEN 'ଜଗତସିଂହପୁର'
    WHEN 16 THEN 'ଝାରସୁଗୁଡ଼ା'
    WHEN 17 THEN 'କଳାହାଣ୍ଡି'
    WHEN 18 THEN 'କନ୍ଧମାଳ'
    WHEN 19 THEN 'କେନ୍ଦ୍ରାପଡ଼ା'
    WHEN 20 THEN 'କେନ୍ଦୁଝର'
    WHEN 21 THEN 'ଖୋର୍ଦ୍ଧା'
    WHEN 22 THEN 'କୋରାପୁଟ'
    WHEN 23 THEN 'ମାଲକାନଗିରି'
    WHEN 24 THEN 'ମୟୂରଭଞ୍ଜ'
    WHEN 25 THEN 'ନବରଙ୍ଗପୁର'
    WHEN 26 THEN 'ନୟାଗଡ଼'
    WHEN 27 THEN 'ନୂଆପଡ଼ା'
    WHEN 28 THEN 'ରାୟଗଡ଼ା'
    WHEN 29 THEN 'ସମ୍ବଲପୁର'
    WHEN 30 THEN 'ସୋନପୁର'
    WHEN 31 THEN 'ସୁନ୍ଦରଗଡ଼'
    ELSE district_name_or
END;

COMMIT;