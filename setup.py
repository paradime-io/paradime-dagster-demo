from setuptools import find_packages, setup

setup(
    name="quickstart_bolt",
    packages=find_packages(exclude=["quickstart_bolt_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "boto3",
        "pandas",
        "matplotlib",
        "textblob",
        "tweepy",
        "wordcloud",
    ],
    extras_require={"dev": ["dagit", "pytest"]},
)
