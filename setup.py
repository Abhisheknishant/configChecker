import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="config-checker",
    version="0.0.1",
    author="Stuart Ianna",
    author_email="stuian@protonmail.com",
    description="Python module wrapper around ConfigParser for enforcing string configuration file operations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stuianna/configChecker",
    classifiers=[
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
    ],
    py_modules=['configchecker'],
    python_requires='>=3.6',
    )
