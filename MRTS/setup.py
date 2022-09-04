import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="holdem-machine-server",
    version="0.0.1",
    author="Python Strategies",
    author_email="pythonstrats@gmail.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pystrats/holdem-machine-server",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy==1.19.1',
        'pandas>=1.1.0',
        'scikit-learn>=0.24.1',
        'tqdm>=4.62.2',
        'apsw>=3.36.0',
        'opencv-python>=4.6.0.66',
        'pillow>=8.3.1',
        'pytesseract>=0.3.10',
        'requests'
   ],
    scripts=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'holdem-machine-server = holdem_machine_server.command_line:main',
            'hms = holdem_machine_server.command_line:main'
        ]
    },
    python_requires='>=3.8',
)
