"""
App Name Extractor for CONFIGO
==============================

Intelligent extraction of app names from natural language input.
Handles various user input patterns and extracts clean app names.
"""

import re
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

class AppNameExtractor:
    """
    Extracts app names from natural language input using NLP techniques.
    """
    
    # Common filler words that should be removed
    FILLER_WORDS = {
        'install', 'get', 'fetch', 'download', 'add', 'setup', 'set', 'up',
        'need', 'want', 'please', 'can', 'you', 'me', 'my', 'the', 'a', 'an',
        'for', 'to', 'with', 'on', 'in', 'at', 'by', 'from', 'of', 'and', 'or',
        'but', 'so', 'if', 'then', 'else', 'when', 'where', 'why', 'how',
        'this', 'that', 'these', 'those', 'i', 'am', 'is', 'are', 'was', 'were',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'shall', 'let', 'make', 'give', 'show',
        'find', 'open', 'run', 'start', 'launch', 'execute', 'use', 'try'
    }
    
    # Common app name mappings for better recognition
    APP_NAME_MAPPINGS = {
        'telegram': 'Telegram',
        'vscode': 'VS Code',
        'visual studio code': 'VS Code',
        'code': 'VS Code',
        'discord': 'Discord',
        'slack': 'Slack',
        'chrome': 'Google Chrome',
        'google chrome': 'Google Chrome',
        'firefox': 'Firefox',
        'mozilla firefox': 'Firefox',
        'zoom': 'Zoom',
        'teams': 'Microsoft Teams',
        'microsoft teams': 'Microsoft Teams',
        'spotify': 'Spotify',
        'steam': 'Steam',
        'obs': 'OBS Studio',
        'obs studio': 'OBS Studio',
        'blender': 'Blender',
        'gimp': 'GIMP',
        'inkscape': 'Inkscape',
        'libreoffice': 'LibreOffice',
        'libre office': 'LibreOffice',
        'thunderbird': 'Thunderbird',
        'mozilla thunderbird': 'Thunderbird',
        'vlc': 'VLC Media Player',
        'vlc media player': 'VLC Media Player',
        'kdenlive': 'Kdenlive',
        'krita': 'Krita',
        'audacity': 'Audacity',
        'handbrake': 'HandBrake',
        'hand brake': 'HandBrake',
        'virtualbox': 'VirtualBox',
        'virtual box': 'VirtualBox',
        'docker': 'Docker',
        'postman': 'Postman',
        'insomnia': 'Insomnia',
        'dbeaver': 'DBeaver',
        'mysql workbench': 'MySQL Workbench',
        'pgadmin': 'pgAdmin',
        'pg admin': 'pgAdmin',
        'mongodb compass': 'MongoDB Compass',
        'mongodb': 'MongoDB Compass',
        'redis': 'Redis Desktop Manager',
        'redis desktop': 'Redis Desktop Manager',
        'tableau': 'Tableau',
        'power bi': 'Power BI',
        'powerbi': 'Power BI',
        'jupyter': 'Jupyter',
        'jupyter lab': 'JupyterLab',
        'jupyterlab': 'JupyterLab',
        'anaconda': 'Anaconda',
        'conda': 'Anaconda',
        'rstudio': 'RStudio',
        'r studio': 'RStudio',
        'matlab': 'MATLAB',
        'octave': 'GNU Octave',
        'gnu octave': 'GNU Octave',
        'scilab': 'Scilab',
        'maxima': 'Maxima',
        'geogebra': 'GeoGebra',
        'geogebra classic': 'GeoGebra',
        'wolfram': 'Wolfram Mathematica',
        'mathematica': 'Wolfram Mathematica',
        'maple': 'Maple',
        'sage': 'SageMath',
        'sagemath': 'SageMath',
        'latex': 'LaTeX',
        'texstudio': 'TeXstudio',
        'tex studio': 'TeXstudio',
        'texmaker': 'TeXmaker',
        'tex maker': 'TeXmaker',
        'overleaf': 'Overleaf',
        'atom': 'Atom',
        'sublime': 'Sublime Text',
        'sublime text': 'Sublime Text',
        'notepad++': 'Notepad++',
        'notepad plus plus': 'Notepad++',
        'brackets': 'Brackets',
        'webstorm': 'WebStorm',
        'intellij': 'IntelliJ IDEA',
        'intellij idea': 'IntelliJ IDEA',
        'pycharm': 'PyCharm',
        'py charm': 'PyCharm',
        'eclipse': 'Eclipse',
        'netbeans': 'NetBeans',
        'net beans': 'NetBeans',
        'android studio': 'Android Studio',
        'xcode': 'Xcode',
        'x code': 'Xcode',
        'visual studio': 'Visual Studio',
        'codeblocks': 'Code::Blocks',
        'code blocks': 'Code::Blocks',
        'dev c++': 'Dev-C++',
        'devcpp': 'Dev-C++',
        'code::blocks': 'Code::Blocks',
        'qt creator': 'Qt Creator',
        'qtcreator': 'Qt Creator',
        'kdevelop': 'KDevelop',
        'kdevelop': 'KDevelop',
        'monodevelop': 'MonoDevelop',
        'mono develop': 'MonoDevelop',
        'sharpdevelop': 'SharpDevelop',
        'sharp develop': 'SharpDevelop',
        'netbeans': 'NetBeans',
        'net beans': 'NetBeans',
        'bluej': 'BlueJ',
        'blue j': 'BlueJ',
        'greenfoot': 'Greenfoot',
        'green foot': 'Greenfoot',
        'drjava': 'DrJava',
        'dr java': 'DrJava',
        'jcreator': 'JCreator',
        'j creator': 'JCreator',
        'jbuilder': 'JBuilder',
        'j builder': 'JBuilder',
        'myeclipse': 'MyEclipse',
        'my eclipse': 'MyEclipse',
        'rational': 'Rational Application Developer',
        'rad': 'Rational Application Developer',
        'websphere': 'WebSphere Application Server',
        'web sphere': 'WebSphere Application Server',
        'jboss': 'JBoss Application Server',
        'wildfly': 'WildFly',
        'wild fly': 'WildFly',
        'tomcat': 'Apache Tomcat',
        'apache tomcat': 'Apache Tomcat',
        'jetty': 'Jetty',
        'glassfish': 'GlassFish',
        'glass fish': 'GlassFish',
        'geronimo': 'Apache Geronimo',
        'apache geronimo': 'Apache Geronimo',
        'karaf': 'Apache Karaf',
        'apache karaf': 'Apache Karaf',
        'activemq': 'Apache ActiveMQ',
        'apache activemq': 'Apache ActiveMQ',
        'kafka': 'Apache Kafka',
        'apache kafka': 'Apache Kafka',
        'spark': 'Apache Spark',
        'apache spark': 'Apache Spark',
        'hadoop': 'Apache Hadoop',
        'apache hadoop': 'Apache Hadoop',
        'hive': 'Apache Hive',
        'apache hive': 'Apache Hive',
        'pig': 'Apache Pig',
        'apache pig': 'Apache Pig',
        'hbase': 'Apache HBase',
        'apache hbase': 'Apache HBase',
        'cassandra': 'Apache Cassandra',
        'apache cassandra': 'Apache Cassandra',
        'couchdb': 'Apache CouchDB',
        'apache couchdb': 'Apache CouchDB',
        'solr': 'Apache Solr',
        'apache solr': 'Apache Solr',
        'lucene': 'Apache Lucene',
        'apache lucene': 'Apache Lucene',
        'mahout': 'Apache Mahout',
        'apache mahout': 'Apache Mahout',
        'storm': 'Apache Storm',
        'apache storm': 'Apache Storm',
        'flink': 'Apache Flink',
        'apache flink': 'Apache Flink',
        'beam': 'Apache Beam',
        'apache beam': 'Apache Beam',
        'airflow': 'Apache Airflow',
        'apache airflow': 'Apache Airflow',
        'nifi': 'Apache NiFi',
        'apache nifi': 'Apache NiFi',
        'kylin': 'Apache Kylin',
        'apache kylin': 'Apache Kylin',
        'superset': 'Apache Superset',
        'apache superset': 'Apache Superset',
        'zeppelin': 'Apache Zeppelin',
        'apache zeppelin': 'Apache Zeppelin',
        'atlas': 'Apache Atlas',
        'apache atlas': 'Apache Atlas',
        'ranger': 'Apache Ranger',
        'apache ranger': 'Apache Ranger',
        'knox': 'Apache Knox',
        'apache knox': 'Apache Knox',
        'ambari': 'Apache Ambari',
        'apache ambari': 'Apache Ambari',
        'hue': 'Apache Hue',
        'apache hue': 'Apache Hue',
        'oozie': 'Apache Oozie',
        'apache oozie': 'Apache Oozie',
        'falcon': 'Apache Falcon',
        'apache falcon': 'Apache Falcon',
        'sentry': 'Apache Sentry',
        'apache sentry': 'Apache Sentry',
        'sqoop': 'Apache Sqoop',
        'apache sqoop': 'Apache Sqoop',
        'flume': 'Apache Flume',
        'apache flume': 'Apache Flume',
        'zookeeper': 'Apache ZooKeeper',
        'apache zookeeper': 'Apache ZooKeeper',
        'curator': 'Apache Curator',
        'apache curator': 'Apache Curator',
        'helix': 'Apache Helix',
        'apache helix': 'Apache Helix',
        'samza': 'Apache Samza',
        'apache samza': 'Apache Samza',
        'heron': 'Apache Heron',
        'apache heron': 'Apache Heron',
        'aurora': 'Apache Aurora',
        'apache aurora': 'Apache Aurora',
        'mesos': 'Apache Mesos',
        'apache mesos': 'Apache Mesos',
        'yarn': 'Apache YARN',
        'apache yarn': 'Apache YARN',
        'tez': 'Apache Tez',
        'apache tez': 'Apache Tez',
        'giraph': 'Apache Giraph',
        'apache giraph': 'Apache Giraph',
        'tika': 'Apache Tika',
        'apache tika': 'Apache Tika',
        'opennlp': 'Apache OpenNLP',
        'apache opennlp': 'Apache OpenNLP',
        'uima': 'Apache UIMA',
        'apache uima': 'Apache UIMA',
        'stanbol': 'Apache Stanbol',
        'apache stanbol': 'Apache Stanbol',
        'jena': 'Apache Jena',
        'apache jena': 'Apache Jena',
        'fuseki': 'Apache Fuseki',
        'apache fuseki': 'Apache Fuseki',
        'clerezza': 'Apache Clerezza',
        'apache clerezza': 'Apache Clerezza',
        'marmotta': 'Apache Marmotta',
        'apache marmotta': 'Apache Marmotta',
        'any23': 'Apache Any23',
        'apache any23': 'Apache Any23',
        'jena': 'Apache Jena',
        'apache jena': 'Apache Jena',
        'fuseki': 'Apache Fuseki',
        'apache fuseki': 'Apache Fuseki',
        'clerezza': 'Apache Clerezza',
        'apache clerezza': 'Apache Clerezza',
        'marmotta': 'Apache Marmotta',
        'apache marmotta': 'Apache Marmotta',
        'any23': 'Apache Any23',
        'apache any23': 'Apache Any23'
    }
    
    @classmethod
    def extract_app_name(cls, user_input: str) -> str:
        """
        Extract clean app name from natural language input.
        
        Args:
            user_input: Raw user input like "get me telegram" or "install discord"
            
        Returns:
            str: Clean app name like "Telegram" or "Discord"
        """
        if not user_input or not user_input.strip():
            return ""
        
        # Convert to lowercase for processing
        input_lower = user_input.lower().strip()
        
        # Remove common prefixes and suffixes
        input_clean = cls._remove_prefixes_and_suffixes(input_lower)
        
        # Split into words and filter out filler words
        words = input_clean.split()
        filtered_words = [word for word in words if word not in cls.FILLER_WORDS]
        
        # Join remaining words
        app_name_raw = ' '.join(filtered_words)
        
        # Apply app name mappings for better recognition
        app_name = cls._apply_app_mappings(app_name_raw)
        
        # Clean up the final app name
        app_name = cls._clean_app_name(app_name)
        
        logger.info(f"Extracted app name: '{user_input}' -> '{app_name}'")
        return app_name
    
    @classmethod
    def _remove_prefixes_and_suffixes(cls, text: str) -> str:
        """
        Remove common prefixes and suffixes from input text.
        
        Args:
            text: Input text to clean
            
        Returns:
            str: Cleaned text
        """
        # Common prefixes to remove
        prefixes = [
            'install', 'get', 'fetch', 'download', 'add', 'setup', 'set up',
            'need', 'want', 'please', 'can you', 'could you', 'would you',
            'i need', 'i want', 'i would like', 'i would love', 'i would appreciate',
            'show me', 'find me', 'give me', 'bring me', 'bring up', 'open up',
            'start up', 'launch', 'run', 'execute', 'use', 'try', 'let me',
            'help me', 'assist me', 'support me', 'enable me', 'allow me'
        ]
        
        # Common suffixes to remove
        suffixes = [
            'please', 'thanks', 'thank you', 'thx', 'app', 'application',
            'program', 'software', 'tool', 'utility', 'package'
        ]
        
        # Remove prefixes
        for prefix in prefixes:
            if text.startswith(prefix + ' '):
                text = text[len(prefix):].strip()
                break
        
        # Remove suffixes
        for suffix in suffixes:
            if text.endswith(' ' + suffix):
                text = text[:-len(suffix)].strip()
                break
        
        return text
    
    @classmethod
    def _apply_app_mappings(cls, app_name: str) -> str:
        """
        Apply app name mappings for better recognition.
        
        Args:
            app_name: Raw app name
            
        Returns:
            str: Mapped app name
        """
        # Check for exact matches first
        if app_name in cls.APP_NAME_MAPPINGS:
            return cls.APP_NAME_MAPPINGS[app_name]
        
        # Check for partial matches
        for key, value in cls.APP_NAME_MAPPINGS.items():
            if app_name in key or key in app_name:
                return value
        
        # If no mapping found, return the original name with proper capitalization
        return app_name.title()
    
    @classmethod
    def _clean_app_name(cls, app_name: str) -> str:
        """
        Clean up the final app name.
        
        Args:
            app_name: App name to clean
            
        Returns:
            str: Cleaned app name
        """
        # Remove extra whitespace
        app_name = ' '.join(app_name.split())
        
        # Handle special cases
        if app_name.lower() in ['vscode', 'vs code', 'visual studio code']:
            return 'VS Code'
        elif app_name.lower() in ['telegram']:
            return 'Telegram'
        elif app_name.lower() in ['discord']:
            return 'Discord'
        elif app_name.lower() in ['slack']:
            return 'Slack'
        elif app_name.lower() in ['chrome', 'google chrome']:
            return 'Google Chrome'
        elif app_name.lower() in ['firefox', 'mozilla firefox']:
            return 'Firefox'
        elif app_name.lower() in ['zoom']:
            return 'Zoom'
        elif app_name.lower() in ['teams', 'microsoft teams']:
            return 'Microsoft Teams'
        elif app_name.lower() in ['spotify']:
            return 'Spotify'
        elif app_name.lower() in ['steam']:
            return 'Steam'
        
        # Default: proper title case
        return app_name.title()
    
    @classmethod
    def validate_app_name(cls, app_name: str) -> bool:
        """
        Validate if the extracted app name is reasonable.
        
        Args:
            app_name: App name to validate
            
        Returns:
            bool: True if app name is valid, False otherwise
        """
        if not app_name or len(app_name.strip()) == 0:
            return False
        
        # Check if app name is too short
        if len(app_name.strip()) < 2:
            return False
        
        # Check if app name contains only common words
        words = app_name.lower().split()
        if len(words) == 1 and words[0] in cls.FILLER_WORDS:
            return False
        
        return True 