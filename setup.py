from distutils.core import setup
setup(
    name = 'faradayio',
    packages = ['faradayio'],
    version = '0.0.1',
    description = 'Asynchronous input/output program linking a network interface and UART port for Faraday radios ',
    author = 'FaradayRF',
    author_email = 'Support@FaradayRF.com',
    url = 'https://github.com/FaradayRF/faradayio',

    license = 'GPLv3',

    classifiers =[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: Ham Radio',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
    ],
)
