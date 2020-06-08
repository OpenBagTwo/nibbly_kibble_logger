from setuptools import setup
import versioneer

setup(name='nibbly_kibble_logger',
      description='Logger for the Nibbly Kibble Raceway',
      author='Gili "OpenBagTwo" Barlev',
      url='https://github.com/OpenBagTwo/nibbly_kibble_logger',
      packages=['nibbly_kibble_logger'],
      license='GPL v3',
      install_requires=[
            "flask>=1.1",
            "click>=5",
            "pyyaml>=5",
      ],
      include_package_data=True,
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass())
