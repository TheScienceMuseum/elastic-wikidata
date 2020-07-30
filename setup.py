import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="elastic-wikidata",
    version="0.0.1",
    author="Science Musuem Group",
    description="elastic-wikidata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheScienceMuseum/elastic-wikidata",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    packages=setuptools.find_packages(),
    py_modules=["cli"],
    entry_points="""
    [console_scripts]
    ew=cli:main
    """,
)
