from django.conf import settings
from sqlalchemy import create_engine


def get_db_engine():
    db = settings.DATABASES['default']
    engine = db['ENGINE']

    if engine == 'django.db.backends.sqlite3':
        return create_engine(f"sqlite:///{db['NAME']}")
    elif engine == 'django.db.backends.postgresql':
        return create_engine(
            f"postgresql://{db['USER']}:{db['PASSWORD']}@{db['HOST']}:{db['PORT']}/{db['NAME']}"
        )
    elif engine == 'mysql.connector.django':
        host = db.get('HOST') or 'localhost'
        port = db.get('PORT') or '3306'
        user = db['USER']
        password = db['PASSWORD']
        name = db['NAME']
        return create_engine(
            f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{name}"
        )
    else:
        raise NotImplementedError(f"Unsupported database engine: {engine}")