import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="elastic-wikidata",
    version="0.2.0",
    author="Science Musuem Group",
    description="elastic-wikidata",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheScienceMuseum/elastic-wikidata",
    download_url="https://github.com/TheScienceMuseum/elastic-wikidata/archive/v0.2.0.tar.gz",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "click==7.1.2",
        "elasticsearch==7.8.1",
        "SPARQLWrapper==1.8.5",
        "tqdm==4.48.2",
        "requests==2.24.0",
    ],
    py_modules=["cli", "elastic_wikidata"],
    entry_points="""
    [console_scripts]
    ew=cli:main
    """,
)
