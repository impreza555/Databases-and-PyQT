from setuptools import setup, find_packages

setup(
    name="geek_mess_server",
    version="0.0.1",
    description="GeekMessenger Server",
    author="impreza555",
    author_email="example@example.com",
    license="GPLv3",
    packages=find_packages(),
    install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome'],
    scripts=['server/server_run']
)
