from setuptools import setup, find_packages


setup(
    name="django_trees",
    version="2.0.1",
    author='imtapps',
    author_email='serveradmin@imtapps.com',
    description='Simple way to create, persist and manipulate reliable tree structures using Django models.',
    long_description=file('README.rst').read(),
    url='https://github.com/imtapps/django_trees',
    install_requires=file('requirements.txt').read(),
    packages=find_packages(exclude=('project', )),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries',
    ]
)
