#!/usr/bin/env sh

# This script is mainly for copy&paste purposes. You're not actually expected to run it,
# but rather to copy and paste individual lines
# Those invocations are the ones that use the default Docker configuration, and ones that were
# used for data collection. Changes may result in stuff being broken.
# More detailed explanations are added for each tool separately.
# You'll probably want to parallelize some of those. Each call is independent, as long as they don't use the same
# project repository. You can clone two repositories for same project and run different tools on them and everything should work fine.

### Data gathering with Docker
# General remarks
# - Docker containers are run with --privileged to enable checkout of Git repositories and writing to mounted reports and workspaces
# this can be solved in a number of different ways: running with specific user, mounting volumes instead of directories,
# changing owners of those repositories. For me this solution was the fastest, but if you're using a shared environment
# and/or don't want/cannot use --privileged, just make sure that the user inside the container can write to workspace, reports and projects
# - Projects are listed in alphabetical order
# - Be careful with MAPREDUCE and HDFS projects - they are a bit tricky, because for PMD and JavaMetrics they require two remotes
# and for JavaMetrics2 they require two runs - one with each of the remotes (so manual adjustment is required). Details are available near their invocations
# - You need to clone the repositories manually. If you want to use JavaMetrics2, clone via SSH.
# If you already cloned via HTTPS, you don't need to clone again - jsut remove the old remote (`git remote remove origin`) and add the new one


## JavaMetrics
# Collection for JavaMetrics is relatively straightforward and doesn't require any extra magic tricks,
# apart from the stuff that is already covered by Python scripts.
# you just need to make sure that the parameters below match what is present in your setup.
# In particular, make sure that there is a java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar in /mnt/tools
# The general pattern for JavaMetrics is (for each PROJECT_NAME):
## sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=${PROJECT_NAME} -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/${PROJECT_NAME}.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# ActiveMQ
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=activemq -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/activemq.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Camel
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=camel -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/camel.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Cassandra
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=cassandra -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/cassandra.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Flink
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=flink -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/flink.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Groovy
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=groovy -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/groovy.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Hadoop
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=hadoop -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/hadoop.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# HBase
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=hbase -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/hbase.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# HDFS -> requires 2 fetched remotes in hadoop-hdfs repository: apache/hadoop-hdfs and apache/hadoop
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=hadoop-hdfs -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/hadoop-hdfs.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Hive
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=hive -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/hive.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Ignite
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=ignite -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/ignite.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Kafka
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=kafka -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/kafka.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Mapreduce -> requires 2 fetched remotes in hadoop-hdfs repository: apache/hadoop-mapreduce and apache/hadoop
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=hadoop-mapreduce -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/hadoop-mapreduce.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Spark
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=spark -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/spark.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Zeppelin
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=zeppelin -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/zeppelin.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Zookeeper
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics -e PROJECT_NAME=zookeeper -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/zookeeper.txt:/opt/config/commits.txt -v /mnt/tools/java-metrics-1.0-SNAPSHOT-jar-with-dependencies.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

## PMD
# Collection for PMD requires a bit of a special setup - an extra jar file in pmd/lib directory
# the jar file is available in binary distribution of reproduction package, or - if you can't access it - you can
# build it from `runners/helpers/pmd/PMDRules` Maven project.
# You'll also need `defect-prediction` repository (this one) cloned, because the ruleset from `runners/helpers/pmd/java-ruleset.xml` is used for metrics collection.
# Rest of the tricky stuff is already covered by Python scripts.
# Of course, you need to make sure that the parameters below match what is present in your setup.
# In particular, make sure that there is a /mnt/tools/pmd-bin-6.53.0 in /mnt/tools, and that it contains the jar file mentioned above
# The general pattern for PMD is (for each PROJECT_NAME):
## sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=${PROJECT_NAME} -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/${PROJECT_NAME}.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# ActiveMQ
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=activemq -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/activemq.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Cassandra
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=cassandra -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/cassandra.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Camel
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=camel -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/camel.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Flink
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=flink -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/flink.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Groovy
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=groovy -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/groovy.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Hadoop
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=hadoop -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/hadoop.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# HBase
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=hbase -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/hbase.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# HDFS -> requires 2 fetched remotes in hadoop-hdfs repository: apache/hadoop-hdfs and apache/hadoop
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=hadoop-hdfs -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/hadoop-hdfs.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Hive
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=hive -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/hive.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Ignite
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=ignite -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/ignite.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Kafka
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=kafka -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/kafka.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Mapreduce -> requires 2 fetched remotes in hadoop-hdfs repository: apache/hadoop-hdfs and apache/hadoop
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=hadoop-mapreduce -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/hadoop-mapreduce.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Spark
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=spark -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/spark.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Zeppelin
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=zeppelin -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/zeppelin.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Zookeeper
sudo docker run --privileged -e METRICS_TOOL_NAME=pmd -e PROJECT_NAME=zookeeper -v $(pwd)/defect-prediction/runners/helpers:/opt/tools/helpers -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/defect-prediction/data/commits/zookeeper.txt:/opt/config/commits.txt -v /mnt/tools/pmd-bin-6.53.0:/opt/ext_tool tomaszlewowski/metric-gathering:1.10


## JavaMetrics2 (aka JavaMetricsPP)
# Collection for JavaMetrics2 is a little tricky, because there are three things to remember about:
# - JavaMetrics2 uses SSH protocol to download old revisions of files from GitHub, which means we need to give it an SSH key
# so that it can connect to GitHub. It also parses the organization-or-user and repository name from remote and assumes that
# the remote is an SSH clone from GitHub (JavaMetrics2 cannot collect data from repositories that are not on GitHub). If
# you have a clone made by HTTPS, you're out of luck - remove the remote (`git remote remove`) and add an SSH one.
# Make sure that your clone only has a single remote set, because otherwise it may try to fetch stuff from a randomly selected one.
# - JavaMetrics2 assumes that repositories are stored in a layout /<root-dir>/<organization-or-user>/<repository-name>
# for example, apache/kafka has to be stored in /home/user/projects/apache/kafka or /opt/apache/kafka
# and if it'll be stored in /opt/repositories/kafka, the calculation will break
# thus we mount not only `/opt/projects` like for PMD and JavaMetrics, but also `/opt/apache` - because all repositories
# analyzed in this research are from `apache` organization. If you use a different one, you'll need to mount a different location,
# e.g. eclipse/milo would go to `/opt/eclipse/mile` and you'd need to mount `/opt/eclipse`.
# - the official release of JavaMetrics2 requires the users to know the positions of classes that will be analyzed prior
# to starting the analysis. This is a little inconvenient, as it would require pre-parsing of Java files before the calculation.
# Make sure you either use the jar file from the reproduction package or apply the patch `patches/javametrics2/no-line-check.patch`
# to JavaMetrics2 repository before building it.
# Rest of the tricky stuff is already covered by Python scripts.
# Of course, you need to make sure that the parameters below match what is present in your setup.
# In particular, make sure that there is a /mnt/tools/javametrics2.jar in /mnt/tools, and that it contains the jar file mentioned above
# The general pattern for JavaMetrics2 is (for each PROJECT_NAME):
## sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=${PROJECT_NAME} -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/${PROJECT_NAME}.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# ActiveMQ
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=activemq -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/activemq.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

#  Cassandra
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=cassandra -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/cassandra.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Camel
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=camel -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/camel.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Flink
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=flink -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/flink.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Groovy
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=groovy -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/groovy.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Hadoop
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=hadoop -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/hadoop.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# HBase
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=hbase -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/hbase.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# HDFS -> requires data to be fetched from two remotes, but only a single one present in the repository - that's why it has to be executed twice, once with origin set to apache/hadoop, second with origin at apache/hadoop-mapreduce
# This has to be the exact same location (unless you're willing to change mounts), because JavaMetricsPP assumes some directory layout based on the repository parameters
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=hadoop-hdfs -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/hadoop-hdfs.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Hive
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=hive -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/hive.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Ignite
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=ignite -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/ignite.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Kafka
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=kafka -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/kafka.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Mapreduce -> requires data to be fetched from two remotes, but only a single one present in the repository - that's why it has to be executed twice, once with origin set to apache/hadoop, second with origin at apache/hadoop-mapreduce
# This has to be the exact same location (unless you're willing to change mounts), because JavaMetricsPP assumes some directory layout based on the repository parameters
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=hadoop-mapreduce -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/hadoop-mapreduce.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Spark
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=spark -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/spark.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Zeppelin
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=zeppelin -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/zeppelin.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10

# Zookeeper
sudo docker run --privileged -e METRICS_TOOL_NAME=javametrics2 -e PROJECT_NAME=zookeeper -v ~/.ssh:/root/.ssh -v $(pwd)/workspace:/opt/workspace -v $(pwd)/reports:/opt/reports -v $(pwd)/projects:/opt/projects -v $(pwd)/projects:/opt/apache -v $(pwd)/defect-prediction/data/commits/zookeeper.txt:/opt/config/commits.txt -v /mnt/tools/javametrics2.jar:/opt/ext_tool tomaszlewowski/metric-gathering:1.10


## Postprocessing
# Once you finished collecting data from the repositories, they are in a layout that isn't exactly user-friendly:
# each results are in `metrics.csv` file in a directory <tool>/<project>/<revision>
# which may mean thousands of metric files. This is not exactly convenient to analyze.
# You can use the following script to merge the metrics on a per-tool basis

# Collecting all metrics for single tool
python metric_joining/project_joiner.py --metrics_root $(pwd)/reports/metrics/pmd --target_file $(pwd)/reports/metrics/pmd/complete_pmd.csv
python metric_joining/project_joiner.py --metrics_root $(pwd)/reports/metrics/javametrics --target_file $(pwd)/reports/metrics/javametrics/complete_javametrics.csv
python metric_joining/project_joiner.py --metrics_root $(pwd)/reports/metrics/javametrics2 --target_file $(pwd)/reports/metrics/javametrics2/complete_javametrics2.csv

python metric_joining/project_joiner.py --metrics_root $(pwd)/smells/reports/metrics/javametrics2 --target_file $(pwd)/smells/reports/metrics/javametrics2/complete_javametrics2.csv

## This is the end of initial data processing. All further operations are run in the modelling flow.
