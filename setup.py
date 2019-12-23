from setuptools import find_packages, setup

setup(
    name='wgadmin',
    version='1.0.0',
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
    }
)
