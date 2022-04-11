from setuptools import setup, find_packages

setup(
    name="harvester",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Click",
        "sickle",
    ],
    entry_points={
        "console_scripts": [
            "harvest=harvester.cli:harvest",
        ]
    },
)
