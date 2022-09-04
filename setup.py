import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MRTS",
    version="1.0.00",
    author="Python Strategies",
    author_email="pythonstrats@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pystrats/mrts",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests>=2.28.1',
        'prettytable>=3.4.1'
   ],
    scripts=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'mrts = MRTS.cl:main'
        ]
    },
    python_requires='>=3.0',
)
