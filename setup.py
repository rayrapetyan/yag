from setuptools import setup, find_packages

setup(
    name='yag',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'ansible @ https://github.com/rayrapetyan/ansible/archive/copy_local_perf_opt.zip',
        'click',
    ],
    entry_points={
        'console_scripts': [
            'yag = yag.cli:cli'
        ]
    },
)
