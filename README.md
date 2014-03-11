machinelearning
===============

Experiments in machine learning for web logs presented at bsides Vancouver 2014. 

The python notebooks can be run via::

  ipython notebook

in the directory where you place the notebooks. 

The mlTail.py program is meant to take incoming logs via stdin and produce a report of 
bad actors after stdin has stopped. 

These tools all use the excellent topic modelling library: gensim available via::

  pip install gensim

-----
Setup
-----
Ideally you should read the presentation and the ipython notebooks. But if you can't wait:

Steps: 
1) Separate your baseline apache logs into good and bad via the goodFromBad.py script: 
./goodFromBad.py <apachelogfilenamegoeshere>
2) Send a sample log into mltail.py: 
cat sample.log| ./mltail.py -c options.conf
3) Bask in the glorious output of machine learning telling you who is attacking you
4) Buy me a beer
