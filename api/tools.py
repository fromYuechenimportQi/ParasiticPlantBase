from pathlib import Path

##拿到path的相应的物种子目录下的gff和fasta文件
def get_gff_and_fasta_under_path(path,species_name):
    path_dict = {}
    suffix_patterns = ['.gff3','.gff','.fasta','.fa']
    species_path = Path.joinpath(path,species_name)
    assert species_path.exists(),f"{species_name} not exists in {path}"
    all_file = [i for i in species_path.iterdir() if i.suffix in suffix_patterns]
    if len(all_file)<2:
        raise RuntimeError(f"Check if your gff3 or fasta in {path}")
    else:
        for i in all_file:
            if i.name == 'genome.fasta' or i.name == "genome.fa":
                path_dict['genome_fasta'] = str(i)
            if i.name == 'genome.gff' or i.name == 'genome.gff3':
                path_dict['genome_gff'] = str(i)
    assert len(path_dict.keys()) == 2,f"Did you forget one of gff3 and fasta in {species_path}?"
    return path_dict


def jbrowse_javascript(species):
    js = '''
    <script>
    var assembly = {
    name: '{species}',
    sequence: {
        type: 'ReferenceSequenceTrack',
        trackId: '{species}-ReferenceSequenceTrack',
        adapter: {
            type: 'BgzipFastaAdapter',
            fastaLocation: {
                uri: '/jbrowse/{species}/genome.fasta.gz1',
                locationType: 'UriLocation',
            },
            faiLocation: {
                uri: '/jbrowse/{species}/genome.fasta.gz.fai',
                locationType: 'UriLocation',
            },
            gziLocation: {
                uri: '/jbrowse/{species}/genome.fasta.gz.gzi',
                locationType: 'UriLocation',
            },
        },
    },};
    var tracks = 
    [
    {
        "type": "FeatureTrack",
        "trackId": "{species}",
        "name": "{species}_Ref",
        "Category": ['Genes'],
        "adapter": {
            "type": "Gff3TabixAdapter",
            "gffGzLocation": {
                "uri": "/jbrowse/{species}/genome.sorted.gff.gz1",
                "locationType": "UriLocation"
            },
            "index": {
                "location": {
                    "uri": "/jbrowse/{species}/genome.sorted.gff.gz.tbi",
                    "locationType": "UriLocation"
                },
                "indexType": "TBI"
            }
        },
        "renderer": {
            "type": 'SvgFeatureRenderer',
        },
        "assemblyNames": ["{species}"]
    }
]
    </script>
'''.replace("{species}",species)
    js_react = '''
    <script type="module">
        const { createViewState, JBrowseLinearGenomeView } =
            JBrowseReactLinearGenomeView
        const { createElement } = React
        const { render } = ReactDOM
        const button = document.getElementById("gene_button")
        console.log(button.dataset.location)
        const state = new createViewState({
            assembly,
            tracks,
            location: button.dataset.location,
            defaultSession: {
                "name": "default session",
                "margin": 0,
                "view": {
                    "id": "linearGenomeView",
                    "minimized": false,
                    "type": "LinearGenomeView",
                    "offsetPx": 50862294,
                    "bpPerPx": 0.07552906018346421,
                    "displayedRegions": [
                        {
                            "refName": "",
                            "start": 0,
                            "end": 4107770,
                            "reversed": false,
                            "assemblyName": "{species}"
                        }
                    ],
                    "tracks": [
                        {
                            "id": "z4k8UHbntL",
                            "type": "FeatureTrack",
                            "configuration": "{species}",
                            "minimized": false,
                            "displays": [
                                {
                                    "id": "RlJMOPZMal",
                                    "type": "LinearBasicDisplay",
                                    "height": 207,
                                    "trackShowLabels": true,
                                    "trackDisplayMode": "normal",
                                    "trackMaxHeight": 200,
                                    "configuration": "{species}-LinearBasicDisplay"
                                }
                            ]
                        },
                        {
                            "id": "TeOFvWvJc",
                            "type": "ReferenceSequenceTrack",
                            "configuration": "{species}-ReferenceSequenceTrack",
                            "minimized": false,
                            "displays": [
                                {
                                    "id": "rbj9h81-g0",
                                    "type": "LinearReferenceSequenceDisplay",
                                    "height": 322,
                                    "configuration": "{species}-ReferenceSequenceTrack-LinearReferenceSequenceDisplay",
                                    "showForward": true,
                                    "showReverse": true,
                                    "showTranslation": true
                                }
                            ]
                        }
                    ],
                    "hideHeader": false,
                    "hideHeaderOverview": false,
                    "hideNoTracksActive": false,
                    "trackSelectorType": "hierarchical",
                    "trackLabels": "overlapping",
                    "showCenterLine": false,
                    "showCytobandsSetting": true,
                    "showGridlines": true
                },
                "widgets": {
                    "hierarchicalTrackSelector": {
                        "id": "hierarchicalTrackSelector",
                        "type": "HierarchicalTrackSelectorWidget",
                        "collapsed": {},
                        "view": "linearGenomeView"
                    },
                }
            }
        });

        render(
            createElement(JBrowseLinearGenomeView, { viewState: state }),
            document.getElementById('jbrowse_linear_genome_view'),
        )
    </script>
    '''.replace('{species}',species)
    return js + js_react
