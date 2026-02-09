DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cendres_vapeur',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3307',
        'CHARSET': 'utf8mb4',
        'COLLATION': 'utf8mb4_unicode_ci',
        'OPTIONS': {
            'autocommit': True,
        }
    }
}
