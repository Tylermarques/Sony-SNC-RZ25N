from setuptools import setup

setup(
    name="SonySNCRZ25N",
    version="1.0.0",
    description="Library for interacting with Sony SNC RZ25N Camera",
    long_description_content_type="text/markdown",
    url="https://github.com/Tylermarques/Sony-SNC-RZ25N",
    author="Tyler Marques",
    author_email="tylermarques@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["SNCRZ25N"],
    include_package_data=True,
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "realpython=reader.__main__:main",
        ]
    },
)