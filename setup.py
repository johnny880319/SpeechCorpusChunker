from setuptools import setup, find_packages

setup(
    name='speech_corpus_builder',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'PyYAML',
        'faster-whisper',
        'torch',
        'torchaudio',
    ],
    entry_points={
        'console_scripts': [
            'scb=main_cli:main'
        ]
    }
)
