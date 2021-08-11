from setuptools import setup, find_packages

setup(
    name="sagesaver",
    version="1.0.0",
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
    package_dir={"": "src"},
    packages=find_packages(where="src"),

    entry_points={
        'console_scripts': [
        ],
    },
    
    python_requires=">=3.6"
)