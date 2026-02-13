DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cendres_vapeur', # Database name
        'USER': '', # Database username
        'PASSWORD': '', # Database password
        'HOST': 'localhost', # Database host, usually 'localhost' or an IP address
        'PORT': '', # Default MySQL port is 3306, but it's left empty here
        'CHARSET': 'utf8mb4',
        'COLLATION': 'utf8mb4_unicode_ci',
        'OPTIONS': {
            'autocommit': True,
        }
    }
}
