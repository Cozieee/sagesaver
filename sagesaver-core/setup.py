from setuptools import setup, find_packages, Command

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
        'pymongo',
        'pymysql',
        'jmespath',
        'cached_property',
        'ec2_metadata'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={
        "": [
            "sagesaver/data/*"
        ]
    },
    python_requires=">=3.6"
)
