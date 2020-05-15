import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = [
    "requests>=2.20.0",
    "urllib3>=1.23",
    "websockets == 8.1",
    "umsgpack == 0.1.0",
]

setuptools.setup(
    name="crs_debuger",
    version="0.3.1",
    author="HuangXiaojun",
    author_email="huangxiaojun@sightp.com",
    description="crs debuger",
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ywyt738/crs_debuger",
    packages=setuptools.find_packages(),
    install_requires=requires,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 1 - Planning",
        "Operating System :: POSIX :: Linux",
    ],
)
