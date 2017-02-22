This is a fork of CliNER intended to work with Python 3.x and OSX

===============================
CliNER
===============================

Clinical Named Entity Recognition system (CliNER) is an open-source natural language processing system for named entity recognition in clinical text of electronic health records.  CliNER system is designed to follow best practices in clinical concept extraction, as established in i2b2 2010 shared task.

CliNER is implemented as a two-pass machine learning system for named entity recognition, currently using a Conditional Random Fields (CRF) classifier to establish concept boundaries and a Support Vector Machine (SVM) classifier to establish the type of concept.

Please note that for optimal performance, CliNER requires the users to obtain a Unified Medical Language System (UMLS) license, since UMLS Metathesaurus is used as one of the knowledge sources for the above classifiers.


* Free software: Apache v2.0 license
* Documentation: http://cliner.readthedocs.org.


Installation
--------

**Cloning the CliNER git repository:**

    git clone https://github.com/text-machine-lab/CliNER.git


**Package Dependencies**

Ensure the following packages are installed on your system.

::

    python-pip
    python-virtualenv
    python-dev
    g++
    make
    gfortran
    libopenblas-dev
    liblapack-dev

For instance, if you do not have gfortran, you can install it  on a Debian-flavored Linux using

    sudo apt-get install gfortran



**Using an installation script**

Linux users can use an installation script to install this project. Note that it cannot get tools and data that require special use agreements (namely, i2b2 data and the UMLS tables), which have to be obtained separately.

To invoke the script, ensure you are in a bash terminal (zsh will not work).

::

    user@your-machine:~$ cd CliNER
    user@your-machine:~/CliNER$ source install.sh


This script is runs just a few simple steps

    1. set the CLINER_DIR environment variable
    2. install python dependencies (via pip)
    3. build the `cliner` command
    4. Download the optional GENIA tagger and update config.txt


**Step-by-step**

    1. **CLINER_DIR** - set the CLINER_DIR env variable to refer to the project base

        export CLINER_DIR=$(pwd)

    2. **Python Dependencies** - install dependencies via pip

        pip install -r requirements.txt

        python -m nltk.downloader maxent_treebank_pos_tagger wordnet punkt

    3. **Build cliner** - build the script for running cliner

        python setup.py install

    4. **GENIA** - this is optional. See OPTIONAL section of readme for more


Please email wboag@cs.uml.edu with your installation issues/questions.


**Diagnostic Script**

We know that software installation can be a major hassle. We hate it too. That's why why made the 'install' directory. This directory contains diagnostic tools to determine what is causing the system installation to fail. We hope you'll never have to use it. To run the full suite of checks, do:

    python install/diagnose.py

Good luck!



**OPTIONAL**


(1) virtualenv

    **Why would I want this?** Virtual environments are good practice for when you want to install particular versions of python packages on a per-project basis. They modify local include paths, rather than the system-wide one. They are especially useful when you do not want to disturb other users on a shared server or when your own projects require different library version numbers.

    Setup a virtual environent, and make sure you specify that we're using Python 2.7

        virtualenv venv_cliner -p /usr/bin/python2.7

    You must re-enable the virtual environment every new session.

        source venv_cliner/bin/activate


    **reference** https://virtualenv.pypa.io/en/latest/


(2) GENIA

    **Why would I want this?** The GENIA tagger is a tool similar to CliNER but designed for Biomedical text. Depending on the domain of your data, this tool's pretrained model may or may not be able to improve performance for CliNER as it detects concepts.

    download the GENIA tagger (use the download script we wrote for this)

        bash install/genia/install_genia.sh

    If you're curious to see how the script works (downloads tarball, fixes typo in genia code, compiles) feel free to open this script up in a text editor.

    **reference** http://www.nactem.ac.uk/tsujii/GENIA/tagger/

    You must edit the file "$CLINER_DIR/config.txt" and change the line saying "GENIA  None" to "GENIA <path to genia executable>".

    This command will do that: sed -i ``sed -i 's|GENIA.*|GENIA '<path of dir containing genia exe>/geniatagger'|g' $CLINER_DIR/config.txt``


(3) UMLS tables

    **Why would I want this?** The UMLS, or Unified Medical Language System, is a very comprehensive database of various medical terms and concepts. Access to it would allow CliNER to leverage domain-specific knowledge.

    SORRY! This resource is contains potentially sensitive clinical data, and requires a confidentiality agreement. We can't do that part for you. Please see "Additional Resources" portion of this readme for instructions on how to obtain the UMLS tables.

    **reference** https://www.nlm.nih.gov/research/umls/quickstart.html


    How to obtain UMLS tables:

        - Download all the files from: https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html
        - Unzip mmsys.zip into a folder and put all other files downloaded into that folder.
        - Execute run_linux.sh and select 'Install UMLS' on gui.
        - Choose a destination for umls directory, hit 'Ok' and then 'Create New Config'.
        - Accept the agreement.
        - Select 'Only Active UMLS Sources' as your default subset.
        - Select 'Done' at the top right of gui pane and then select 'Begin Subset'.
        - This process may take a while, the directory '<Destination_Directory_Path>/<UMLS VERSION>/META' should contain the necessary files needed.


Out-of-the-Box Model
--------

Although i2b2 licensing prevents us from releasing our cliner models trained on i2b2 data, we generated some comprable models from automatically-annotated MIMIC II text.

This silver MIMIC model can be found at https://github.com/text-machine-lab/CliNER/blob/master/models/mimic-silver.cliner.tgz





Additional Resources
--------

These are resources that require login credentials to access secure data, so we can't provide you with them directly.


(1) Get i2b2 2010 shared task data

    The Data Use and Confidentiality Agreement (DUA) with i2b2 forbids us from redistributing the i2b2 data. In order to gain access to the data, you must go to:

    https://www.i2b2.org/NLP/DataSets/AgreementAR.php

    to register and sign the DUA. Then you will be able to request the data through them.




(2) UMLS tables

    In order to use the UMLS tables, you must request a license. See:

    http://www.nlm.nih.gov/databases/umls.html

    You will need to get following tables: **MRREL.RRF, MRCONSO.RRF, MRSTY.RRF**

    **Put these tables in the $CLINER_DIR/umls_tables directory.**

    In order to tell CliNER that the tables are there, you must edit the file "$CLINER_DIR/config.txt" and change the line saying "UMLS  None" to "UMLS <path to dir containing tables>".

    This command will do that: ``sed -i 's|UMLS.*|UMLS '<path of dir containing umls tables>'|g' $CLINER_DIR/config.txt``

    **The database will be built from the tables when CliNER is run for the first time.**




Example Data
--------

Although we cannot provide i2b2 data, there is a sample to demonstrate how the data is formatted (not actual data from i2b2, though).

    examples/pretend.txt

This is a text file. Discharge summaries are written out in plaintext, just like this. It is paired with a concept file, which has its annotations.

    examples/pretend.con

This is a concept file. It provides annotations for the concepts (problems, treatments, and tests) of the text file. The format is as follows - each instance of a concept has one line. The line shows the text span, the line number, token numbers of the span (delimited by white space), and the label of the concept.

    examples/pretend.xml

This is an alternative way to annotate concepts from a discharge summary. This format is easier to read in context because the concepts are embedded in the text document. Note that the .xml files still function as a concept file and will always be paried with a corresponding text file (despite redundancies).




Usage
--------

Here are some use cases:

(1) Check that CliNER installed correctly

This help message will list the options available to run (train/predict/evaluate)

    cliner --help


(2) See an end-to-end run of train/predict/evaluate

This script demonstrates a simple run of training, predicting, and evaluating the system.

   bash examples/demo.sh


(3) Training

These examples demonstrate how to build a CliNER model which can then be used for predicting concepts in text files.

    cliner train examples/pretend.txt --annotations examples/pretend.con --format i2b2 --model models/foo.model

This example trains a very simple CliNER model. The (pretend.txt, pretend.con) pair form as the only document for learning to identify concepts. We must specify that these files are i2b2 format (even though the .con extension implies i2b2 format, you can never be too careful). The CliNER model is then serialized to models/foo.model as specified.

Please note that multiple files could be passed by enclosing them as a glob within "" quotes.


    cliner train examples/pretend.txt --annotations examples/pretend.con --format i2b2 --model models/foo.model --grid-search

This example doesn't actually run. The input file pretend.con is too small that there are not enough data points to perform a grid search over. However, if you do wish to run grid search, it is as simple as using the --grid-search flag.


    cliner train examples/pretend.txt --annotations examples/pretend.xml --format xml --model models/foo.model

Here's one last example for training. In this example, we trained on xml-annotated data. Hopefully it's now clear why we always pair the .xml file with a .txt (it makes the interface much more consistent across data formats).


(4) Prediction

Once your CliNER model is built, you can use it to predict concepts in text files.

    cliner predict examples/pretend.txt --out data/test_predictions/ --format i2b2 --model models/foo.model

In this example, we use the models/foo.model CliNER model that we built up above. This model is used to predict concepts in i2b2 format for the pretend.txt file. This generates a file named "pretend.con" and stores it in the specified output directory.

Notice that we trained and predicted on the same file, so we definitely overfit our way into a perfect match.

    cliner predict examples/pretend.txt --out data/test_predictions/ --format xml  --model models/foo.model

Once again, here's the same example as above, but with predicting xml annotations.


(5) Evaluation

This allows us to evaluate how well CliNER does by comparing it against a gold standard.

    cliner evaluate examples/pretend.txt --gold examples --predictions data/test_predictions/ --format i2b2

Evaluate how well the system predictions did for given discharge summaries. The prediction and reference driectories are provided with the --predictions and --gold flags, respectively. Both sets of data must be in the same format, and that format must be specified - in this case, they are both i2b2. This means that both the examples and data/test_predictions directories contain the file pretend.con.


(6) Re-formatting (NOT WORKING)

    cliner format examples/pretend.txt --annotations data/test_predictions/pretend.con --format xml

WARNING! This functionality is not up-to-date. If you try to run the format command, it will likely just crash and give you an ugly error message. It's on our TODO list, we promise! In theory, this example would produce the xml-annotations that correspond to the concepts described in pretend.con.



(7) Run unit tests

SORRY! [this section is under construction, unfortunately]




Deploying with Vagrant
--------

With Vagrant and a type-2 hypervisor (such as the free VirtualBox) installed on
the system, running "vagrant up" will deploy a virtual machine and painlessly
install/build CliNER.

The access ip is listed during deployment (usually 127.0.0.1:2222).
The username/password is vagrant/vagrant.



