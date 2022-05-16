from setuptools import setup, find_packages

setup(
    name="geek_mess_client",
    version="0.0.1",
    description="GeekMessenger Client",
    author="impreza555",
    author_email="example@example.com",
    license="GPLv3",
    packages=find_packages(),
    install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome'],
    scripts=['client/client_run']
)
