import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='cadcadgolem',
    version='0.2.0',
    author='Roger van Schie',
    author_email='rogervs@protonmail.com',
    description='A cadCAD workload dispatcher to the Golem network',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/rogervs/cadcadgolem',
    packages=setuptools.find_packages(include=['cadcadgolem']),
    install_requires=[
        'cadcad',
        'yapapi'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8.5',
)
