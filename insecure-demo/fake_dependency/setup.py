from setuptools import setup, find_packages

setup(
    name="fake_dependency",
    version="0.1",
    packages=find_packages(),
    description="A fake dependency to demonstrate vulnerabilities",
    author="BlackJack",
    license="MIT"
)
