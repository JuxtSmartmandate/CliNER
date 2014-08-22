#
# install.sh
#
# Purpose: This is a demo that will install CliCon and it's package dependencies
#
# Note: This does not download/install:
#        1) i2b2 data
#        2) UMLS tables
#


function get_genia {
    # save current path
    old_path=$(pwd)

    # Get sources
    cd $CLICON_DIR/clicon/features_dir/genia
    wget http://www.nactem.ac.uk/tsujii/GENIA/tagger/geniatagger-3.0.1.tar.gz
    tar xzvf geniatagger-3.0.1.tar.gz

    # Build GENIA tagger
    cd geniatagger-3.0.1/
    echo "$(sed '1i#include <cstdlib>' morph.cpp)" > morph.cpp # fix build error
    make

    # Successful build ?
    if ! [[ $? -eq 0 ]] ; then
        echo "there was a build error in GENIA"
        return
    fi

    # Set config file location of tagger
    config_file="$CLICON_DIR/config.txt"
    out_tmp="out.tmp.txt"
    echo "GENIA $(pwd)/geniatagger" > $out_tmp
    while read line ; do
        if ! [[ $line = GENIA* ]] ; then
            echo $line >> $out_tmp
        fi
    done < "$config_file"
    mv $out_tmp $config_file

    # return to original path
    cd $old_path
}



# Ensure resources are available
which g++ gfortran virtualenv pip
resources=$?
if [[ $resources -eq 0 ]] ; then


    # CLICON_DIR must be defined before proceeding
    if [[ "$CLICON_DIR" = "" ]] ; then

        CLICON_DIR="$( cd "$( dirname "$0" )" && pwd )"
        export CLICON_DIR=\"$CLICON_DIR\"
        echo -e "export CLICON_DIR=\"$CLICON_DIR\"" >> .bashrc

    fi


    # Create virtual environment
    virtualenv venv_clicon
    source venv_clicon/bin/activate


    # Install python dependencies
    pip install nltk numpy scikit-learn scipy python-crfsuite
    python -m nltk.downloader maxent_treebank_pos_tagger wordnet


    # Download & install GENIA tagger
    get_genia


    # Install 'clicon' script for command line usage
    python setup.py install


else

    echo -e "\n\tError: Not all resources available on system."
    echo -e "\nPlease ensure the following packages are installed:"

    packages=(g++ gfortran python-dev python-pip python-virtualenv libopenblas-dev liblapack-dev)
    for p in ${packages[@]} ; do
        echo -e "\t$p"
    done
    echo ""

fi
