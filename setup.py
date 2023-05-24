from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='optimized_minimizer',
    url='https://github.com/mathias77515/optimized_minimizer',
    author='Mathias Regnier',
    author_email='mathias.p.regnier@gmail.com',
    # Needed to actually package something
    packages=['optimized_minimizer'],
    # Needed for dependencies
    install_requires=['numpy'],
    # *strongly* suggested for sharing
    version='0.1',
    # The license can be anything you like
    license='',
    description='Optimized minimizer for MPI python.',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)