from setuptools import setup, find_packages

setup(
    name="sagesaver-core",
    version="0.1.2",
    author="Victor Lin",
    author_email="vvictor.llin@gmail.com",
    description="Utils for SageSaver server scripts",
    url="https://github.com/Cozieee/sagesaver/sagesaver-core",
    project_urls={
        "Project Main": "https://github.com/Cozieee/sagesaver",
    },
    install_requires=[
        'boto3',
        'click',
        'pymongo',
        'jmespath'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    include_package_data=True,
    packages=find_packages(where=""),

    entry_points={
        'console_scripts': [
            'sagesaver = sagesaver.cli.entrypoint:main',
        ],
    },
    
    python_requires=">=3.6"
)