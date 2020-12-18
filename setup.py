from setuptools import setup, find_packages

setup(
    name='yag',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'ansible-base @ git+https://github.com/rayrapetyan/ansible@optimize_local_copy_stable_2_10',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'yag = yag.cli:cli'
        ]
    },
)
