from setuptools import find_packages, setup

setup(
    name='wgadmin',
    version='0.0.0',
    author="Arti Zirk",
    author_email="arti@zirk.me",
    description="WireGuard VPN Administration interface",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.5',
    install_requires=[
        'Flask',
        'Flask-WTF',
        'Flask-SQLAlchemy'
    ],
    extras_require={
        'dev': ['Flask-Testing']
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: System :: Networking',
        'Intended Audience :: System Administrators',
        'Framework :: Flask'
    ]

)
