from setuptools import setup

setup(
   name='project-33t',
   version='0.1',
   description='vinyl album covers recognition',
   author='Steven BOEHM',
   author_email='steven.boehm.dev@gmail.com',
   packages=['project-33t'],
   install_requires=[
       'numpy==1.20',
       'scipy==1.6',
       'flask==2.0.0',
       'elasticsearch==8.3.3',
       'scikit-image==0.19',
       'Pillow==9.0.0',
       'CairoSVG==2.5.2',
       'six==1.16.0',
       'testresources==2.0.1'
   ],
   scripts=[
       'src/scripts/import-covers.py',
       'src/scripts/feed-elastic.py',
   ]
)
