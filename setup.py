from setuptools import setup, find_packages

setup(
    name='AutoEditor',
    version='0.1',
    packages=find_packages(),
    python_requires='>=3.6, <4',
    install_requires=[
        'tqdm',
        'pvleopard',
        'openai',
        'nltk',
        'pytest',
        'simple-websocket',
        'pydub',
        'Django',
    ],
    extras_require={
        'dev': [
            'pytest>=3.7',
        ],
    },
)
