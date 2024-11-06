import setuptools
import subprocess
import os

firerequests_version = (
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)

if "-" in firerequests_version:
    # when not on tag, git describe outputs: "1.3.3-22-gdf81228"
    # pip has gotten strict with version numbers
    # so change it to: "1.3.3+22.git.gdf81228"
    # See: https://peps.python.org/pep-0440/#local-version-segments
    v,i,s = firerequests_version.split("-")
    firerequests_version = v + "+" + i + ".git." + s

assert "-" not in firerequests_version
assert "." in firerequests_version

assert os.path.isfile("firerequests/version.py")
with open("firerequests/VERSION", "w", encoding="utf-8") as fh:
    fh.write("%s\n" % firerequests_version)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt') as fh:
    requirements = fh.read().splitlines()

setuptools.setup(
    name="firerequests",
    version=firerequests_version,
    author="Rishiraj Acharya",
    author_email="heyrishiraj@gmail.com",
    description="High-Performance Asynchronous HTTP Client setting Requests on Fire 🔥",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rishiraj/firerequests",
    packages=setuptools.find_packages(),
    package_data={"firerequests": ["VERSION"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "fr=firerequests.main:main",
        ],
    },
    install_requires=requirements,
)
