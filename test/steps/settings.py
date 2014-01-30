# Use in-memory databases so tests run fast

DATABASE = 'testing'

BACKEND = {
    'backend': 'sqlite_memory',
    'debug': False
}