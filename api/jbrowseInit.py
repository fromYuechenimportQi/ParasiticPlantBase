## gff manipulate
## awk '$1 ~ /^#/ {print $0;next} {print $0 | "sort -t\"\t\" -k1,1 -k4,4n"}' genome.gff > genome.sorted.gff
## bgzip genome.sorted.gff
## tabix genome.sorted.gff.gz
## mv genome.sorted.gff.gz genome.sorted.gff.gz1

##fasta manipulate
##bgzip -i genome.fasta
##samtools faidx genome.fasta.gz
##mv genome.fasta.gz genome.fasta.gz1

import subprocess
import time
from pathlib import Path
from tools import get_gff_and_fasta_under_path
import argparse
## 首先得到Jbrwose的路径
def get_jbrowse_path():
    BASE_DIR = Path(__file__).resolve().parent.parent
    jbrowse_path = Path('jbrowse/')
    path_pattern = Path.joinpath(BASE_DIR,jbrowse_path)
    assert path_pattern.exists(),f"{path_pattern} not exists"
    return path_pattern



def gff_manipulate(genome_gff_path):
    prefix_of_bash = time.time_ns()
    parent_path = Path(genome_gff_path).parent

    
    temp_bash_name = f'sort_{str(prefix_of_bash)}.sh'
    bash_file = Path.joinpath(parent_path,temp_bash_name)
    with open(bash_file,'w') as f:
        f.write(r'''awk '$1 ~ /^#/ {print $0;next} {print $0 | "sort -t\"\t\" -k1,1 -k4,4n"}' '''
                +f"{genome_gff_path} > {Path.joinpath(parent_path,'genome.sorted.gff')}")
    print("### GFF sorting and indexing start!!!!!")
    #运行bash，对genome.gff进行排序，输出genome.sorted.gff
    print("Sorting gff....")
    subprocess.Popen(f'bash {bash_file}',shell=True).wait()

    #压缩genome.sorted.gff得到genome.sorted.gff.gz
    print("Compressing genome.sorted.gff......")
    subprocess.Popen(f'bgzip {Path.joinpath(parent_path,"genome.sorted.gff")}',shell=True).wait()
    #对genome.sorted.gff.gz文件建索引
    print("indexing sorted.gff.gz......")
    subprocess.Popen(f'tabix {Path.joinpath(parent_path,"genome.sorted.gff.gz")}',shell=True).wait()
    #重命名
    print("Renaming......")
    subprocess.Popen(f'mv {Path.joinpath(parent_path,"genome.sorted.gff.gz")} {Path.joinpath(parent_path,"genome.sorted.gff.gz1")}',
                     shell=True).wait()
    #最后删除temp.sh文件
    print("Removing sort.sh...")
    subprocess.Popen(f'rm {bash_file}',shell=True).wait()
    print("### GFF sorting and indexing done!!!!!")

def fasta_manipulate(genome_fasta_path):
    parent_path = Path(genome_fasta_path).parent

    print("### fasta compressing and indexing start!!!!!")
    print("Compressing fasta......")
    subprocess.Popen(f"bgzip -i {genome_fasta_path}",shell=True).wait()
    print("Indexing fasta......")
    subprocess.Popen(f"samtools faidx {genome_fasta_path}.gz",shell=True).wait()
    print("Renaming......")
    subprocess.Popen(f"mv {genome_fasta_path}.gz {genome_fasta_path}.gz1",shell=True).wait()
    print("### fasta compressing and indexing done!!!!!")
    
def main():
    parser = argparse.ArgumentParser(description='JBrowse Initialization Tool')
    parser.add_argument('species_name', type=str, help='Name of the species')

    args = parser.parse_args()
    jbrowse_path = get_jbrowse_path()  
    
    path_dict = get_gff_and_fasta_under_path(jbrowse_path,args.species_name)
    gff_manipulate(path_dict['genome_gff'])
    fasta_manipulate(path_dict['genome_fasta'])
#main()