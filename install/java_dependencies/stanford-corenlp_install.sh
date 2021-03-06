
if [ "$CLINER_DIR" == "" ];
then
    echo "CLINER_DIR not set..."
    exit
fi

# download files and setup proper directories
wget http://nlp.stanford.edu/software/stanford-corenlp-full-2015-12-09.zip

mv stanford-corenlp-full-2015-12-09.zip $CLINER_DIR/cliner/lib/java/stanford_nlp/

cd $CLINER_DIR/cliner/lib/java/stanford_nlp

unzip stanford-corenlp-full-2015-12-09.zip

mv stanford-corenlp-full-2015-12-09 stanford-corenlp-full

# compile stanford java library
bash runner.sh compile

