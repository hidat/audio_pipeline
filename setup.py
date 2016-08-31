from setuptools import setup, find_packages


setup(name='audio_pipeline',
      version='1.0',
      description='A set of tools to help ingest audio files into asset management systems.',
      author="Heather",
      author_email='cephalopodblue@gmail.com',
      packages=find_packages(),
      scripts=["FileWalker.py", "TomatoBanana.py", "review_parser.py"],
      install_package_data=True,
      install_requires=['yattag', 'mammoth', 'pyyaml', 'musicbrainzngs',
                        'mutagen', 'smartsheet-python-sdk', 'pyacoustid'])
