from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in zkconnector/__init__.py
from zkconnector import __version__ as version

setup(
	name="zkconnector",
	version=version,
	description="connect to zk devices",
	author="Ahmed",
	author_email="Ahmed751995@riseup.net",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
