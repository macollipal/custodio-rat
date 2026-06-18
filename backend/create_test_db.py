import psycopg2

# Connect to Neon QA - create test database
conn = psycopg2.connect(
    '***REMOVED***/neondb?sslmode=require'
)
conn.autocommit = True
cur = conn.cursor()

# Check if test db exists
cur.execute("SELECT 1 FROM pg_database WHERE datname = 'custodio_test'")
exists = cur.fetchone()
if not exists:
    cur.execute('CREATE DATABASE custodio_test')
    print('Created custodio_test database')
else:
    print('custodio_test already exists - will reset it')

cur.close()
conn.close()

# Now connect to custodio_test and create all tables
print('Creating schema in custodio_test...')
conn2 = psycopg2.connect(
    '***REMOVED***/custodio_test?sslmode=require'
)
conn2.autocommit = True
cur2 = conn2.cursor()

# Create all tables by importing the models
import os
os.environ['ENV'] = 'test'
os.environ['DATABASE_URL'] = '***REMOVED***/custodio_test?sslmode=require'

# Import all models to register them with Base
from app.database.database import Base, engine
from app.models import (
    company, rat, user, audit_log, user_company, breach, eipd,
    consentimiento, rubro, rats_sugerido, solicitud_derecho,
    token_blacklist, solicitud_token,
    tkt_solicitud_derecho, tkt_nota, tkt_adjunto, tkt_historial,
    tkt_plantilla, tkt_regla_asignacion,
    asesor,
)

# Create all tables
Base.metadata.create_all(bind=engine)
print('Schema created successfully in custodio_test')

cur2.close()
conn2.close()
print('Done!')
