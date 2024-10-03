import setuptools

with open("README.md", "r",encoding="utf-8") as f:
    long_description = f.read()
    
setuptools.setup(
    name = "ansiparser",
    version = "0.0.1",
    author = "vHrqO",
    author_email="author@example.com",
    description="A convenient library for converting ANSI escape sequences into text or HTML.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bubble-tea-project/ansiparser",                                         
    packages=setuptools.find_packages(),     
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10'
    )