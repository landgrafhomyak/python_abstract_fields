from setuptools import setup

setup(
    name="abstract_fields",
    version="0.1",
    packages=["abstract_fields"],
    description="Mechanism for asserting abstract fields in subclasses",
    package_data={"abstract_fields": ["py.typed", "__init__.pyi"]},
    url="https://github.com/LandgrafHomyak/python_abstract_fields",
    author="Andrew Golovashevich",
    download_url="https://github.com/LandgrafHomyak/python_abstract_fields/releases/tag/v0.1",
    python_requires=">=3.8, <=3.11",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
        "Typing :: Typed"
    ],
    license="MIT",
    license_files=["LICENSE"],
)