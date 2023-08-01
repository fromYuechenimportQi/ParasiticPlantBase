from callDjango import DjangoAPIBase
from genomeParser import SeqParser,GFFParser,GFFInformation,mRNAInformation
import asyncio
from datetime import datetime
DjangoAPIBase().call_django()
from PPBWidgets import models

async def write_mRNA_info_to_database(mRNA:mRNAInformation,gene:models.Gene):
    transcript_id = mRNA.mRNA_id
    transcript_location = mRNA.mRNA_location
    transcript_seq = mRNA.mRNA_seq
    total_cds_seq = mRNA.total_cds_seq
    protein_seq = mRNA.protein_seq

    upstream_3k_location = mRNA.upstream_3k
    upstream_3k_seq = mRNA.upstream_3k_seq

    five_prime_UTR_locations = mRNA.five_prime_UTR
    five_prime_UTR_seqs = mRNA.five_prime_UTR_seqs

    cds_locations = mRNA.cds
    cds_seqs = mRNA.cds_seqs

    intron_locations = mRNA.introns
    intron_seqs = mRNA.intron_seqs

    three_prime_UTR_locations = mRNA.three_prime_UTR
    three_prime_UTR_seqs = mRNA.three_prime_UTR_seqs

    downstream_3k_location = mRNA.downstream_3k
    downstream_3k_seq = mRNA.downstream_3k_seq

    gene = gene
    transcript = models.Transcript(transcript_id=transcript_id,
                                    transcript_location=transcript_location,
                                    transcript_seq=transcript_seq,
                                    total_cds_seq=total_cds_seq,
                                    protein_seq=protein_seq,
                                    upstream_3k_location=upstream_3k_location,
                                    upstream_3k_seq=upstream_3k_seq,
                                    five_prime_UTR_locations=five_prime_UTR_locations,
                                    five_prime_UTR_seqs=five_prime_UTR_seqs,
                                    cds_locations=cds_locations,
                                    cds_seqs=cds_seqs,
                                    intron_locations=intron_locations,
                                    intron_seqs=intron_seqs,
                                    three_prime_UTR_locations=three_prime_UTR_locations,
                                    three_prime_UTR_seqs=three_prime_UTR_seqs,
                                    downstream_3k_location=downstream_3k_location,
                                    downstream_3k_seq=downstream_3k_seq,
                                    gene=gene)
    transcript.save()
    print(f"{str(datetime.now()).split('.')[0]} {transcript_id} is done!")

async def write_gene_info_to_database(gff_info_with_seq:GFFInformation,species:models.Species):
    gene_id = gff_info_with_seq.gene_id
    gene_location = gff_info_with_seq.gene_location
    chromosome = gff_info_with_seq.chromosome
    gene_strand = gff_info_with_seq.strand
    gene_seq = gff_info_with_seq.gene_seq
    species = species
    gene_name = gff_info_with_seq.gene_name
    gene_alias = gff_info_with_seq.gene_alias
    gene_fullname = gff_info_with_seq.gene_fullname
    gene = models.Gene(chromosome = chromosome,
                       gene_strand = gene_strand,
                       gene_location = gene_location,
                       gene_id = gene_id,
                       gene_name = gene_name,
                       gene_alias = gene_alias,
                       gene_fullname = gene_fullname,
                       gene_seq = gene_seq,
                       species = species
                       )
    gene.save()
    print(f"{str(datetime.now()).split('.')[0]} {gene_id} is done!")
    for mRNA in gff_info_with_seq.mRNA:
        await write_mRNA_info_to_database(mRNA,gene=gene)

async def main(gff_info_with_seqs,species:str,max_parallel=56):
    species = models.Species(species_name=species)
    species.save()
    chunks = [gff_info_with_seqs[i:i+max_parallel] for i in range(0, len(gff_info_with_seqs), max_parallel)]
    for chunk in chunks:
        tasks = []
        for task in chunk:
            tasks.append(asyncio.create_task(write_gene_info_to_database(task,species=species)))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    gff_info = GFFParser("/lustre/home/wu_lab/Database/Maize/KN5585/Zea_mays_KN5585.gff").parse()
    gff_info_with_seqs = SeqParser('/lustre/home/wu_lab/Database/Maize/KN5585/Zea_mays_KN5585.fa',gff_info).get_sequence_from_GFFInformation()
    species = "Zea_mays_KN5585"
    asyncio.run(main(gff_info_with_seqs=gff_info_with_seqs,species=species))
    #print(chunks)