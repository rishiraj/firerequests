import setuptools
import subprocess
import os

fastrequests_version = (
    subprocess.run(["git", "describe", "--tags"], stdout=subprocess.PIPE)
    .stdout.decode("utf-8")
    .strip()
)

if "-" in fastrequests_version:
    # when not on tag, git describe outputs: "1.3.3-22-gdf81228"
    # pip has gotten strict with version numbers
    # so change it to: "1.3.3+22.git.gdf81228"
    # See: https://peps.python.org/pep-0440/#local-version-segments
    v,i,s = fastrequests_version.split("-")
    fastrequests_version = v + "+" + i + ".git." + s

assert "-" not in fastrequests_version
assert "." in fastrequests_version

assert os.path.isfile("fastrequests/version.py")
with open("fastrequests/VERSION", "w", encoding="utf-8") as fh:
    fh.write("%s\n" % fastrequests_version)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt') as fh:
    requirements = fh.read().splitlines()

setuptools.setup(
    name="fastrequests",
    version=fastrequests_version,
    author="Rishiraj Acharya",
    author_email="heyrishiraj@gmail.com",
    description="FastRequests: High-Performance Asynchronous HTTP Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rishiraj/fastrequests",
    packages=setuptools.find_packages(),
    package_data={"fastrequests": ["VERSION"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    # entry_points={"console_scripts": ["fastrequests = fastrequests.main:coming_soon"]},
    install_requires=requirements,
)