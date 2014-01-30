# Exit if any command returns a non-zero exit code
set -e

if [ $# -ne 3 ]
then
    echo "Usage: $0 database_name corpus_dir output_file"
    exit
fi

MYSQL_USER=`python -c "from domainmodeller import settings; print settings.BACKEND['user']"`
MYSQL_PASS=`python -c "from domainmodeller import settings; print settings.BACKEND['password']"`
mysql -u $MYSQL_USER --password=$MYSQL_PASS <<< "CREATE DATABASE IF NOT EXISTS \`$1\`;"
CMD="domainmodeller -D $1"
$CMD clear_storage
$CMD import_directory $2
$CMD extract_terms
$CMD create_topics min_occ=1
$CMD topic_stats
$CMD entity_classes > $3
