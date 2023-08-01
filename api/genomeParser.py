#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Date:21/3/2023

from BCBio import GFF
import json
from Bio import SeqIO
from Bio import Seq


class GFFInformation():
    def __init__(self,gene_id:str="",gene_location:str="",chromosome:str="",strand:str="",gene_alias="",gene_fullname="",gene_name="",mRNA:list=None):
        self.gene_id = gene_id
        self.gene_location = gene_location
        self.chromosome=chromosome
        self.strand = strand
        self.mRNA = mRNA
        self.gene_alias = gene_alias
        self.gene_fullname = gene_fullname
        self.gene_name = gene_name
    def __str__(self):
        return f'''Gene_ID: {self.gene_id}
Gene_Location: {self.gene_location}
Strand:{self.strand}
Chromosome:{self.chromosome}
mRNA count: {len(self.mRNA)}'''

class mRNAInformation():
    def __init__(self,mRNA_id,mRNA_location,upstream_3k:str=None,five_prime_UTR:dict=None,cds:dict=None,introns:dict=None,three_prime_UTR:dict=None,downstream_3k:str=None):
        self.mRNA_id = mRNA_id
        self.mRNA_location = mRNA_location
        self.upstream_3k = upstream_3k
        self.five_prime_UTR = json.dumps(five_prime_UTR)
        self.cds = json.dumps(cds)
        self.introns = json.dumps(introns)
        self.three_prime_UTR = json.dumps(three_prime_UTR)
        self.downstream_3k = downstream_3k
    def __str__(self):
        return f'''mRNA_id: {self.mRNA_id} 
        has {len(json.loads(self.five_prime_UTR))} five_prime_UTRs, 
        {len(json.loads(self.cds))} cds,
        {len(json.loads(self.introns))} introns,
        {len(json.loads(self.three_prime_UTR))} three_prime_UTRs
            mRNA_location: {self.mRNA_location},
            upstream_3k: {self.upstream_3k},
            five_prime_UTRs: {self.five_prime_UTR},
            cds: {self.cds},
            introns: {self.introns},
            three_prime_UTRs: {self.three_prime_UTR}.
            downstream_3k: {self.downstream_3k}
         '''
class GFFParser():
    def __init__(self,gff_file:str):
        self.__gff_file = gff_file

    def __set_gene_info(self,feature,gff_info:GFFInformation) -> GFFInformation:
        gff_info.gene_location = f'{int(feature.location.start)+1}-{int(feature.location.end)}'
        gff_info.strand = "+" if feature.strand == 1 else "-"
        gff_info.gene_id = feature.id
        return gff_info


    def __sort_mRNA_sub_features(self,mRNA_sub_features,strand):
        return sorted([i for i in mRNA_sub_features if i.type != 'exon'],
                                                   key=lambda x: int(x.location.start) + 1, reverse=False if strand=="+" else True)


    def parse(self):
        gff_info_list = []
        with open(self.__gff_file,"r") as in_handle:
            for rec in GFF.parse(in_handle):
                for gene in rec.features:
                    gff_info = GFFInformation(chromosome=rec.id)
                    gff_info = self.__set_gene_info(gene,gff_info)
                    mRNA_list = []
                    for mRNA in gene.sub_features:
                        if gff_info.strand == "+":
                            upstream_3k = f'{max(1,int(mRNA.location.start) + 1 - 3000)}-{int(mRNA.location.start) + 1 -1}'
                            downstream_3k = f'{int(mRNA.location.end) + 1}-{int(mRNA.location.end) + 1 + 3000}'
                        else :
                            upstream_3k = f'{int(mRNA.location.end) + 3000}-{int(mRNA.location.end) + 1}'
                            downstream_3k = f'{max(1,int(mRNA.location.start) + 1 - 3000)}-{int(mRNA.location.start) + 1 - 1}'
                        sorted_mRNA_subfeatures = self.__sort_mRNA_sub_features(mRNA.sub_features,gff_info.strand)
                        intron_location, intron_count = {}, 0
                        five_UTR_location,cds_location,three_UTR_location, = {}, {}, {},
                        five_UTR_count, cds_count, three_UTR_count = 0,0,0
                        ## 处理utr和从ds
                        for mRNA_subfeature in sorted_mRNA_subfeatures:
                            if mRNA_subfeature.type == "five_prime_UTR":
                                five_UTR_count += 1
                                five_UTR_location[f'{mRNA_subfeature.id}_{five_UTR_count}'] = f'{mRNA_subfeature.location.start + 1}-{mRNA_subfeature.location.end}'
                            if mRNA_subfeature.type == "CDS":
                                cds_count += 1
                                cds_location[
                                    f'{mRNA_subfeature.id}_{cds_count}'] = f'{mRNA_subfeature.location.start + 1}-{mRNA_subfeature.location.end}'
                            if mRNA_subfeature.type == "three_prime_UTR":
                                three_UTR_count += 1
                                three_UTR_location[
                                    f'{mRNA_subfeature.id}_{three_UTR_count}'] = f'{mRNA_subfeature.location.start + 1}-{mRNA_subfeature.location.end}'

                        ##快慢指针处理mRNA_subfeatrues,得到intron
                        for faster in range(1,len(sorted_mRNA_subfeatures)):
                            slower = faster - 1
                            if gff_info.strand == "+":
                                if sorted_mRNA_subfeatures[slower].location.end != sorted_mRNA_subfeatures[faster].location.start:
                                    ##正链情况下，若下一个subfeature的起始位点与当前的终止位点不匹配，则标记为intron
                                    intron_count += 1
                                    ##intron的位置就是slower.end和faster.start之间的距离,slower.end+1 : faster.start-1
                                    ##GFF.parse返回对象，真实位置会在location.start的基础上-1，因此不用-
                                    intron_location[f'{mRNA.id}_intron_{intron_count}'] = f'{sorted_mRNA_subfeatures[slower].location.end+1 }-{sorted_mRNA_subfeatures[faster].location.start}'

                            else:
                                if sorted_mRNA_subfeatures[slower].location.start != sorted_mRNA_subfeatures[faster].location.end:
                                    intron_count += 1
                                    intron_location[
                                        f'{mRNA.id}_intron_{intron_count}'] = f'{sorted_mRNA_subfeatures[faster].location.end + 1}-{sorted_mRNA_subfeatures[slower].location.start }'

                        mRNA_information = mRNAInformation(mRNA_id=mRNA.id,
                                                           mRNA_location=f'{int(mRNA.location.start) + 1}-{int(mRNA.location.end)}',
                                                           five_prime_UTR=five_UTR_location,
                                                           cds = cds_location,
                                                           introns = intron_location,
                                                           three_prime_UTR=three_UTR_location,
                                                           upstream_3k = upstream_3k,
                                                           downstream_3k= downstream_3k)
                        mRNA_list.append(mRNA_information)
                    gff_info.mRNA = mRNA_list
                    gff_info_list.append(gff_info)
        return gff_info_list

class SeqParser():
    def __init__(self,genome_fasta,gff_info):
        self.genome_dict = {}
        self.gff_info = gff_info
        for seq_record in SeqIO.parse(genome_fasta,'fasta'):
            self.genome_dict[seq_record.id] = str(seq_record.seq)
    def __loc_seq_transformer(self,location,chromosome):
        [start, end] = map(lambda x: int(x), location.split('-'))
        if start > end:
            start,end = end,start
        sequence = self.genome_dict[chromosome][start - 1:end]
        return sequence
    def get_sequence_from_GFFInformation(self):
        gene_with_seqs = []
        for gene in self.gff_info:
            # handle gene location
            gene_sequence = self.__loc_seq_transformer(gene.gene_location,gene.chromosome)
            setattr(gene,'gene_seq',gene_sequence)

            for mRNA in gene.mRNA:
                upstream_3k_seq, five_prime_UTR_seqs, cds_seqs, intron_seqs, three_prime_UTR_seqs, downstream_3k_seq = "", {}, {}, {}, {}, ""
                upstream_3k_seq = self.__loc_seq_transformer(mRNA.upstream_3k, gene.chromosome)
                downstream_3k_seq = self.__loc_seq_transformer(mRNA.downstream_3k, gene.chromosome)
                total_cds = ""
                need_to_set = {"upstream_3k_seq":upstream_3k_seq,
                               "five_prime_UTR_seqs":five_prime_UTR_seqs,
                               "cds_seqs":cds_seqs,
                              "intron_seqs":intron_seqs,
                              "three_prime_UTR_seqs":three_prime_UTR_seqs,
                              "downstream_3k_seq":downstream_3k_seq}
                mRNA_sequence = self.__loc_seq_transformer(mRNA.mRNA_location,gene.chromosome)
                setattr(mRNA,'mRNA_seq',mRNA_sequence)

                for id,location in json.loads(mRNA.five_prime_UTR).items():
                    five_prime_UTR_seqs[id] = self.__loc_seq_transformer(location,gene.chromosome)
                for id,location in json.loads(mRNA.cds).items():
                    cds_seqs[id] = self.__loc_seq_transformer(location,gene.chromosome)
                for id,location in json.loads(mRNA.introns).items():
                    intron_seqs[id] = self.__loc_seq_transformer(location,gene.chromosome)
                for id,location in json.loads(mRNA.three_prime_UTR).items():
                    three_prime_UTR_seqs[id] = self.__loc_seq_transformer(location,gene.chromosome)
                for k,v in need_to_set.items():
                    if isinstance(v,dict):
                        setattr(mRNA,k,json.dumps(v))
                    else:
                        setattr(mRNA,k,v)

                for seq in cds_seqs.values():
                    if gene.strand == "-":
                        #如果是负链，则反向互补链
                        total_cds += str(Seq.Seq(seq).reverse_complement())
                    else:
                        total_cds += seq
                setattr(mRNA,'total_cds_seq',total_cds)

                protein_seq = Seq.Seq(total_cds).translate()
                setattr(mRNA,'protein_seq',protein_seq)

            gene_with_seqs.append(gene)
        return gene_with_seqs

if __name__ == "__main__":
    gff = GFFParser("./test.gff")
    output = gff.parse()
    gene_with_seqs = SeqParser('B73_chr1.fa',output).get_sequence_from_GFFInformation()
    # print(gene_with_seqs[1].mRNA[0].five_prime_UTR_seqs)
    # print(gene_with_seqs[1].mRNA[0].cds_seqs)
    # print(gene_with_seqs[1].mRNA[0].intron_seqs)
    # print(gene_with_seqs[1].mRNA[0].three_prime_UTR_seqs)
    for gene in gene_with_seqs:
        print(f"{gene.gene_id}:\n")
        for mRNA in gene.mRNA:
            print(mRNA.mRNA_id,mRNA.total_cds)
            print(mRNA.protein_seq)
            print(isinstance(mRNA.total_cds,str))
