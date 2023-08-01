
from genomeParser import GenomeParser
from callDjango import DjangoAPIBase


class proteinParser(DjangoAPIBase):
    def __init__(self, fasta):
        '''
            输入: protein.fa
            输出: dict
        '''
        self.__prot_fasta = fasta

    def parse(self):
        return GenomeParser(genome_fasta=self.__prot_fasta, gff="foo").read_fasta()

    def save_in_db(self):
        prot_dic = self.parse()
        self.call_django()
        from PPBWidgets import models
        transcripts = models.Transcript.objects.filter(prot="")
        for transcript in transcripts:
            print(f"Saving {transcript.transcript_id}....")
            transcript.prot = prot_dic[transcript.transcript_id]
            transcript.save()

class cdsParser(proteinParser):
    def save_in_db(self):
        import json
        self.call_django()
        from PPBWidgets import models
        cds_dic = self.parse()
        transcripts = models.Transcript.objects.all()
        for transcript in transcripts:
            temp_cds = json.loads(transcript.cds)
            temp_cds["cds_total"] = cds_dic[transcript.transcript_id]
            transcript.cds = json.dumps(temp_cds)
            transcript.save()
    

if __name__ == "__main__":
    prot_fasta = "/lustre/home/wu_lab/Database/Maize/KN5585/protein.fa"
    cds_fasta = "/lustre/home/wu_lab/Database/Maize/KN5585/cds.fa"
    import os
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          "ParasiticPlantsBase.settings")
    django.setup()
    from PPBWidgets.models import *
    # ins = proteinParser(prot_fasta=prot_fasta)
    # ins.save_in_db()
    ins = cdsParser(fasta=cds_fasta)
    ins.save_in_db()
    