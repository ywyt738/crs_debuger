import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="crs_debuger",
    version="0.0.3",
    author="HuangXiaojun",
    author_email="huangxiaojun@sightp.com",
    description="crs debuger",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ywyt738/crs_debuger",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 1 - Planning",
        "Operating System :: POSIX :: Linux",
    ],
)
