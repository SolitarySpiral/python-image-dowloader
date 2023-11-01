"""Setup package for py-pi"""

from setuptools import setup


setup(
    name='python-nozomi',
    packages=['nozomi'],
    version='2.0.0',
    license='MIT',
    description='Nozomi API for retrieving images, videos, gifs.',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author='Alfa_Q',
    author_email='alfakyuu@gmail.com',
    url='https://github.com/Alfa-Q/python-nozomi',
    download_url='https://github.com/Alfa-Q/python-nozomi/archive/2.0.0.tar.gz',
    keywords=['nozomi', 'nozomi.la', 'api', 'video', 'image', 'anime'],
    install_requires=[
        'requests',
        'dacite',
    ],
    extras_require={
        'dev': [
            'pytest'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires=">=3.7"
)
