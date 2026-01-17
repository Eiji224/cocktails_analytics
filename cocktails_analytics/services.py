from django.conf import settings
from sqlalchemy import create_engine


def get_db_engine():
    db = settings.DATABASES['default']
    if db['ENGINE'] == 'django.db.backends.sqlite3':
        return create_engine(f"sqlite:///{db['NAME']}")
    elif db['ENGINE'] == 'django.db.backends.postgresql':
        return create_engine(
            f"postgresql://{db['USER']}:{db['PASSWORD']}@{db['HOST']}:{db['PORT']}/{db['NAME']}"
        )
    elif db['ENGINE'] == 'django.db.backends.mysql':
        return create_engine(
            f"mysql+pymysql://{db['USER']}:{db['PASSWORD']}@{db['HOST']}:{db['PORT']}/{db['NAME']}"
        )
    else:
        raise NotImplementedError("Unsupported database engine")