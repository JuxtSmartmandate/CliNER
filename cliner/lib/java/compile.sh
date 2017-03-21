
JAVA_DIR="$CLINER_DIR/cliner/lib/java"

METAMAP_DIR="$JAVA_DIR/metamap"
STANFORD_DIR="$JAVA_DIR/stanford_nlp"
LVG_DIR="$JAVA_DIR/lvg_norm"
#OPEN_NLP_DIR="$JAVA_DIR/openNLP"

ENTRY_POINT_DIR="$JAVA_DIR/entry_point"

cd $LVG_DIR
bash "runner.sh" compile

cd $METAMAP_DIR
bash "runner.sh" compile

cd $STANFORD_DIR
bash "runner.sh" compile

#cd $OPEN_NLP_DIR
#bash "runner.sh" compile

cd $ENTRY_POINT_DIR
bash "runner.sh" compile
