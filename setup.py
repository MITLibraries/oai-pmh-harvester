from setuptools import find_packages, setup

setup(
    name="harvester",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click", "sickle", "smart_open"],
    entry_points={
        "console_scripts": [
            "oai=harvester.cli:main",
        ]
    },
)
