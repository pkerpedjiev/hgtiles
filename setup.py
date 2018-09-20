from setuptools import setup

install_requires = [
    'cython',
    'numpy',
    'pysam',
    'h5py',
    'pandas',
    'slugid',
    'git+https://github.com/nvictus/pybbi.git',
    'cooler'
]

setup(
    name='hgtiles',
    version='0.2.12',
    description='Tile loading for higlass-server',
    author='Peter Kerpedjiev',
    author_email='pkerpedjiev@gmail.com',
    url='',
    install_requires=install_requires,
    packages=['hgtiles'],
)
