from setuptools import setup, find_packages

setup(
    name='facility-bot',
    version='0.1.0',
    url="https://github.com/Craeckie/facility-bot",
    description="Erstellt Temperaturdiagramme und zeigt Müllabfuhr-Zeiten an",
    packages=find_packages(),
    #long_description=open('README.md').read(),
    #long_description_content_type="text/markdown",
    zip_safe=False,

    install_requires=[
        'python-telegram-bot',
        'redis',
        'pyzbar',
        'python-dateutil',
        'requests',
        'phonenumbers',
        'vobject',
        'beautifulsoup4',
        'matplotlib',
        'icalendar',
        'flask',
    ]
)
