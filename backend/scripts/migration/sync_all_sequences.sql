-- Sincroniza todas las secuencias de PostgreSQL (Neon) con el valor máximo de cada tabla.
-- Ejecutar en el panel de Neon (Supabase dashboard o psql) cada vez que se migré o reinicie la BD.

SELECT setval('rats_id_seq', (SELECT MAX(id) + 1 FROM rats));
SELECT setval('audit_logs_id_seq', (SELECT MAX(id) + 1 FROM audit_logs));
SELECT setval('companies_id_seq', (SELECT MAX(id) + 1 FROM companies));
SELECT setval('users_id_seq', (SELECT MAX(id) + 1 FROM users));
SELECT setval('eipds_id_seq', (SELECT MAX(id) + 1 FROM eipds));
SELECT setval('security_breaches_id_seq', (SELECT MAX(id) + 1 FROM security_breaches));
SELECT setval('consentimientos_id_seq', (SELECT MAX(id) + 1 FROM consentimientos));
SELECT setval('rats_sugeridos_id_seq', (SELECT MAX(id) + 1 FROM rats_sugeridos));
SELECT setval('user_companies_id_seq', (SELECT MAX(id) + 1 FROM user_companies));
SELECT setval('rubros_id_seq', (SELECT MAX(id) + 1 FROM rubros));
