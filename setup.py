from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

packages = find_packages()

setup(
    name='docker-optimizer',
    version='1.0.0',
    description='A small program to optimize Dockerfiles',
    long_description=readme,
    author='Bogdan Mustiata',
    author_email='bogdan.mustiata@gmail.com',
    license='BSD',
    entry_points={
        "console_scripts": [
            "docker-optimizer = docker_optimizer.mainapp:main"
        ]
    },
    install_requires=[],
    packages=packages,
    package_data={
        '': ['*.txt', '*.rst'],
        'docker_optimizer': ['py.typed'],
    })
