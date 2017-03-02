#
# Willie Boag            wboag@cs.uml.edu
#
# CliNER - smart_install.sh
#
# NOTE: Must be run with 'source'
#
# 'install' directory
BASE_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

export CLINER_DIR=$BASE_DIR

# set CLINER_INSTALL_DIR variable
source $BASE_DIR/install/cliner_dir/set_cliner_dir.sh
echo "Setting dir done"

# python dependencies (use source because of virtualenv)
# source $BASE_DIR/install/dependencies/install_python_dependencies.sh

# install 'cliner' command
bash $BASE_DIR/install/build_cliner/build_cliner.sh
echo "Installing cliner done"

# genia tagger
bash $BASE_DIR/install/genia/install_genia.sh
echo "Installing genia done"

# install stanford parser
bash $BASE_DIR/install/java_dependencies/stanford-corenlp_install.sh
echo "Installing stanford parser done"

