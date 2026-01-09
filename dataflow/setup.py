from setuptools import setup, find_packages

setup(
    name="traceit-dataflow",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "psycopg2-binary>=2.9.9",
    ],
)
