domainmodeller is a Python/Java pipeline for term extraction, entity class extraction and DBPedia entity linking.

Requirements
============

- Java 7 (OpenJDK or Sun JDK)
- MySQL
- RabbitMQ

Installation
============

Build Java services:

```
cd javaservices/
./build.sh
```

Install python dependencies:

```
python setup.py develop
```

Test that the above worked:

```
domainmodeller
```

For verbose documentation:

```
domainmodeller help
```

Configure database details in ```domainmodeller/settings.py```

Run
===

Start services:

```
./start_celery.sh

./start_java_services.sh
```

Then run tasks, e.g.

```
domainmodeller clear_storage
domainmodeller import_directory /path/of/text/files
domainmodeller extract_terms
domainmodeller create_topics
domainmodeller topic_stats
domainmodeller entity_classes > /tmp/entityclasses.csv
```

(The above process is encapsulated in ```scripts/entityclass_process.sh```)

Term extraction
===============

The term extraction Java web service can be used as a standalone API. It runs on 
```http://localhost:8082``` and has a basic web interface at that address to
let you get familiar with the output. The term extraction algorithms require 
a domain model to work (a file with a list of context words for a particular 
domain). A generic domain model is provided in ```domainmodels/default.txt```.

Entity class extraction
=======================

Entity classes are nouns that describe types of entities for a domain. For example,
entity classes in the tourism domain would be "hotel", "pool", "reception" and so on.

The entity class extraction process is encapsulated in ```scripts/entityclass_process.sh```.

DBPedia Entity Linking
======================

Extracted topics can be linked to DBPedia entities. This task requires running a standalone
Solr lookup service which can be found here (README included):
http://vm-unlp-demos.deri.ie/apache2-default/files/solrservices.tar.gz

License
=======

Licensed under AGPLv3.

```
    domainmodeller program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    domainmodeller is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero Public License for more details.

    You should have received a copy of the GNU Affero Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
```

