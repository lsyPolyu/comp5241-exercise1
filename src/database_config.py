"""Choose the local SQLite database or the configured PostgreSQL database."""

import os


def database_uri(root_dir):
    configured_url = os.environ.get('DATABASE_URL', '').strip()
    if configured_url:
        if configured_url.startswith('postgres://'):
            configured_url = 'postgresql+psycopg2://' + configured_url[len('postgres://'):]
        elif configured_url.startswith('postgresql://'):
            configured_url = 'postgresql+psycopg2://' + configured_url[len('postgresql://'):]
        elif not configured_url.startswith('postgresql+psycopg2://'):
            raise ValueError('DATABASE_URL must be a PostgreSQL connection URL.')
        return configured_url

    if (os.environ.get('NOTETAKER_VERCEL') == '1'
            or os.environ.get('VERCEL') == '1'
            or os.environ.get('VERCEL_ENV')):
        raise RuntimeError('DATABASE_URL is required on Vercel; SQLite is only for local development.')

    db_path = os.path.join(root_dir, 'database', 'app.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return f'sqlite:///{db_path}'
