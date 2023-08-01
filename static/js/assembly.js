export default {
    name: 'Cuscuta_v1.1',
    sequence: {
        type: 'ReferenceSequenceTrack',
        trackId: 'Cuscuta-ReferenceSequenceTrack',
        adapter: {
            type: 'BgzipFastaAdapter',
            fastaLocation: {
                uri: '/jbrowse/Cuscuta_australis/Cuscuta.genome.v1.1.fasta.gz1',
                locationType: 'UriLocation',
            },
            faiLocation: {
                uri: '/jbrowse/Cuscuta_australis/Cuscuta.genome.v1.1.fasta.gz.fai',
                locationType: 'UriLocation',
            },
            gziLocation: {
                uri: '/jbrowse/Cuscuta_australis/Cuscuta.genome.v1.1.fasta.gz.gzi',
                locationType: 'UriLocation',
            },
        },
    },
}

