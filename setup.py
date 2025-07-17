import setuptools

with open("readme.md", "r", encoding="utf-8") as ff:
    long_description = ff.read()

setuptools.setup(
    name='phtool',
    version='0.25.713',
    author='Dr Jie Zheng & Dr Lin-Qiao Jiang',
    author_email='jiezheng@nao.cas.cn',
    description='Photometry Tools', # short description
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/drjiezheng/phtool',
    # packages=setuptools.find_packages(),
    packages=['phtool', ],
    include_package_data=True,
    entry_points={
        'console_scripts': ['phtool = phtool.__main__:main',],
    },
    # package_data={"phtool": ["default.*", "bright.*",]},
    python_requires='>=3.10',
    classifiers=[
        # "Development Status :: 5 - Production/Stable",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    install_requires=['numpy', 'scipy', 'matplotlib', 
        'astropy', 'photutils', 'astroalign',
        'tqdm', 'qastutil', 'qmatch']
)
