from setuptools import setup, find_packages
import versioneer

setup(
    name='fortius-ant',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='FortiusANT',
    author='Sebastien Laclau',
    author_email='seb.laclau@gmail.com',
    #package_dir={'fortiusant':'fortiusant'},
    packages=['fortius_ant'],
    package_data={
        'fortius_ant':['./*'],
    },
    entry_points={
        'console_scripts': [
            'fortius-ant=fortius_ant.FortiusAnt:main',
        ],
    },
    data_files=[
        ("/share/applications",["fortius-ant.desktop"])
    ],
)
