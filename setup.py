import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slack_bot",
    author="Peter Newstein",
    author_email="peternewstein@gmail.com",
    description="A bot which calculates the rent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pnewstein/slack_bot",
    packages=["slack_bot"],
    python_requires=">=3.10",
    install_requires=["slack-sdk", "pytest"],
)
