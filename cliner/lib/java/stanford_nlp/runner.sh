#!/bin/bash

STANFORD_CORENLP_DEPENDENCIES=":stanford-corenlp-full/*"
DEPENDENCY_PARSER_DEPENDENCIES=$STANFORD_CORENLP_DEPENDENCIES

compile() {

    echo "compiling DependencyParser.java"
    javac -cp $DEPENDENCY_PARSER_DEPENDENCIES DependencyParser.java -d .
    echo "finished compiling DependencyParser.java"

}

run() {

    java -cp $DEPENDENCY_PARSER_DEPENDENCIES "parser.DependencyParser"

}

clean() {

    rm -r parser
    rm *.pyc

}

if [ "$1" == "compile" ]; then

    compile

elif [ "$1" == "run" ]; then

    run

elif [ "$1" == "clean" ] ;then

    clean

else

    echo -en "valid flags:\n\tcompile\n\trun\n\tclean\n"

fi

# EOF

