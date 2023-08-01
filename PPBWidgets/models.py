from django.db import models

# Create your models here.

'''
models is for "M" in "MTV"
directly related to the data base
'''


class Species(models.Model):
    species_name = models.CharField(max_length=50)


class Gene(models.Model):
    chromosome = models.CharField(max_length=10)
    gene_strand = models.CharField(max_length=10)
    gene_location = models.CharField(max_length=50, blank=True) #'5000-6000'
    gene_id = models.CharField(max_length=50)
    gene_name = models.CharField(max_length=100)
    gene_alias = models.CharField(max_length=100)
    gene_fullname = models.CharField(max_length=100)
    gene_seq = models.TextField()
    species = models.ForeignKey(Species, on_delete=models.CASCADE)


class Transcript(models.Model):
    transcript_id = models.CharField(max_length=50)
    transcript_location = models.CharField(max_length=50) #'5000-6000'
    transcript_seq = models.TextField() 
    total_cds_seq = models.TextField()
    protein_seq = models.TextField()

    upstream_3k_location = models.TextField()
    upstream_3k_seq = models.TextField()

    five_prime_UTR_locations = models.TextField() #json '{"UTR.1":"5000-5008","UTR.2":"6000-6004",...}'
    five_prime_UTR_seqs = models.TextField() #json '{"UTR.1":"CACACTA","UTR.2":"ACACA",...}'

    cds_locations = models.TextField() #json same as above
    cds_seqs = models.TextField() #json, same as above

    intron_locations = models.TextField() #json
    intron_seqs = models.TextField() #json

    three_prime_UTR_locations = models.TextField() #json
    three_prime_UTR_seqs = models.TextField() #json

    downstream_3k_location = models.TextField()
    downstream_3k_seq = models.TextField()

    gene = models.ForeignKey(Gene, on_delete=models.CASCADE)


class BlastDB(models.Model):
    description = models.CharField(max_length=50)
    # description字段需要严格填写，该字段与前端显示blast db相匹配
    type = models.CharField(max_length=20)
    path = models.CharField(max_length=100)
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
