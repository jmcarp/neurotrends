from setuptools import setup, find_packages

setup(
    name='neurotrends',
    version='0.1',
    packages=find_packages(),
    package_data={'' : ['data/*', 'maplib/*']},
    include_package_data=True,
)
