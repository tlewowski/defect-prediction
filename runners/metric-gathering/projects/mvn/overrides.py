CMD_OVERRIDES = {
    'tomee-project': [
        '-Pquick',
        '-Dsurefire.useFile=false',
        '-DdisableXmlReport=true',
        '-DuniqueVersion=false',
        '-ff',
        '-Dassemble',
        '-DskipTests',
        '-DfailIfNoTests=false',
        'clean',
        'compile'
    ]
}