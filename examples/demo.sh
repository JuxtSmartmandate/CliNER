#!/bin/sh


# Train model on an xml-formatted file
# Note, 'examples' directory only has one xml file (but cliner accepts globs)
python cliner/train.py -t "$CLINER_DIR/examples/pretend.txt" -c "$CLINER_DIR/examples/pretend.con" -f i2b2 -m "$CLINER_DIR/examples/example_model_dir/example.model"
echo "DONE"
#cliner train "$CLINER_DIR/examples/*.txt" --annotations "$CLINER_DIR/examples/*.xml" --format xml


# Use trained model to predict concepts for a given txt file
# Note, 'examples' directory only has one txt file (but cliner accepts globs)
#cliner predict "$CLINER_DIR/examples/*.txt" --out $CLINER_DIR/data/test_predictions/ --format i2b2 --model "$CLINER_DIR/examples/example_model_dir/example.model"
#cliner predict "$CLINER_DIR/examples/*.txt" --out $CLINER_DIR/data/test_predictions/ --format xml


# Evaluate how well the system classified.
# Note, in this case it is 100% because it trained/predicted on the same file.
#cliner evaluate "$CLINER_DIR/examples/pretend.txt" --gold $CLINER_DIR/examples --predictions $CLINER_DIR/data/test_predictions/ --format i2b2
