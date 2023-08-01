export default [
    {
        "type": "FeatureTrack",
        "trackId": "Cuscuta",
        "name": "Cuscuta_Ref",
        "Category": ['Genes'],
        "adapter": {
            "type": "Gff3TabixAdapter",
            "gffGzLocation": {
                "uri": "/jbrowse/Cuscuta_australis/Cuscuta.v1.1.sorted.gff3.gz1",
                "locationType": "UriLocation"
            },
            "index": {
                "location": {
                    "uri": "/jbrowse/Cuscuta_australis/Cuscuta.v1.1.sorted.gff3.gz.tbi",
                    "locationType": "UriLocation"
                },
                "indexType": "TBI"
            }
        },
        "renderer": {
            "type": 'SvgFeatureRenderer',
        },
        "assemblyNames": ["Cuscuta_v1.1"]
    }
]