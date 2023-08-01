from django.http import HttpResponse, JsonResponse,FileResponse
from django.views.decorators.cache import cache_control
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import *
from api.blastTools import Blast
from django.conf import settings    
from django.db.models.query import QuerySet
import json
from api.tools import jbrowse_javascript
from pathlib import Path
'''
views is for "V" in "MTV"
the most important key component in the website
Code logic of a web page should be done here
'''
## Home对应index()
## Home的物种图片对应search_species()
## Search对应search()
## Search的结果对应search_result()
## blast对应blast()
## blast结果对应blast_result()
## jbrowse对应jbrowse()

## 如果要针对性改变某个页面的功能逻辑，请按照上述对应关系修改视图函数代码
## 若需要暂停某模块，可以在模块的视图函数的第一句加入return HttpResponse(request,"Somthing went wrong on this page")，其余部分注释掉
# links["Cuscuta_australis"] = 'https://www.ncbi.nlm.nih.gov/genome/70252?genome_assembly_id=384097'
# links['Orobanche_cumana'] = 'https://ngdc.cncb.ac.cn/gwh/Assembly/24468/show'
# links['Phelipanche_aegyptiaca'] = 'https://ngdc.cncb.ac.cn/gwh/Assembly/24467/show'
# links['Lindenbergia_luchunensis'] = 'https://ngdc.cncb.ac.cn/gwh/Assembly/24466/show'
# links['Gastrodia_elata'] = 'https://ngdc.cncb.ac.cn/gwh/Assembly/21458/show'
class SpeciesInformation:
    def __init__(self,photo_static_path:str,species_name:str,download_link:str,example:str):
        self.static_path = photo_static_path
        self.species_name = species_name
        self.download_link = download_link
        self.search_example = example
species_infos = [SpeciesInformation('img/Cuscuta_australis(南方菟丝子).jpg','Cuscuta australis','https://www.ncbi.nlm.nih.gov/genome/70252?genome_assembly_id=384097','C000N0045E0'),
                SpeciesInformation('img/Orobanche_cumana(向日葵列当).jpg','Orobanche cumana','https://ngdc.cncb.ac.cn/gwh/Assembly/24468/show','T78542N0C00G00032'),
                SpeciesInformation('img/Phelipanche_aegyptiaca.jpg','Phelipanche aegyptiaca','https://ngdc.cncb.ac.cn/gwh/Assembly/24467/show','T99112N1C0000G00024'),
                SpeciesInformation('img/Lindenbergia_luchunensis(钟萼草).jpg','Lindenbergia luchunensis','https://ngdc.cncb.ac.cn/gwh/Assembly/24466/show','T1829N0C01G00006'),
                SpeciesInformation('img/Gastrodia_elata.jpg','Gastrodia elata','https://ngdc.cncb.ac.cn/gwh/Assembly/21458/show','GelC01G00029'),
                #SpeciesInformation('img/哆啦_A梦.jpg','Zea mays KN5585','https://www.KN5585.com'),
                ]

def index(request):
    return render(request,'index.html',{"species_info":species_infos})

def search_species(request,species):
    species_info = None
    for info in species_infos:
        if info.species_name == species or info.species_name == species.replace('_',' '):
            species_info = info
    if request.method == "GET":
        return render(request,'search_species.html',{'species':species,'search_result':'','species_info':species_info})
    elif request.method == "POST":
        query = request.POST["gene_id"]
        msg = ''
        ## 先拿到通过搜索species_name得到species_obj
        species_obj = Species.objects.filter(species_name=species).first()
        ## 尝试模糊搜索基因ID
        result = Gene.objects.filter(species=species_obj,gene_id__icontains=query)
        
        ## 如果没搜到，则试图模糊搜索转录本ID，并通过转录本ID得到基因ID
        if not len(result):
            ## 为了保证返回QuerySet，再对gene_id进行一次搜索
            temp =Transcript.objects.filter(transcript_id__icontains=query).first()
            ## 如果没找到则temp为None
            if temp is not None:
                result = Gene.objects.filter(species=species_obj,gene_id=temp.gene.gene_id)
        elif len(result) >= 50:
            total_length = len(result)
            result = result[:50]
            msg = f"{total_length} results are found, only 50 results will be showed."
        return render(request,'search_species.html',{'species':species,'search_result':result,'msg':msg,'species_info':species_info})
    
def search(request):
    if request.method == "GET":
        return render(request,'search.html',{'search_result':''})
    elif request.method == "POST":
        query = request.POST["gene_id"]
        msg = ''
        ## 先拿到通过搜索species_name得到species_obj
        #species_obj = Species.objects.filter(species_name=species).first()
        ## 尝试模糊搜索基因ID
        result = Gene.objects.filter(gene_id__icontains=query)
        
        ## 如果没搜到，则试图模糊搜索转录本ID，并通过转录本ID得到基因ID
        if not len(result):
            ## 为了保证返回QuerySet，再对gene_id进行一次搜索
            temp =Transcript.objects.filter(transcript_id__icontains=query).first()
            ## 如果没找到则temp为None
            if temp is not None:
                result = Gene.objects.filter(gene_id=temp.gene.gene_id)
        elif len(result) >= 50:
            total_length = len(result)
            result = result[:50]
            msg = f"{total_length} results are found, only 50 results will be showed."
        return render(request,'search.html',{'search_result':result,'msg':msg})


def search_result(request, gene_id):
    import json
    gene = Gene.objects.filter(gene_id=gene_id).first()
    if not gene:
            try:
                gene_id = Transcript.objects.filter(
                    transcript_id__icontains=gene_id).first().gene.gene_id
                gene = Gene.objects.get(gene_id=gene_id)
            except:
                pass
    species_name = gene.species.species_name
    


    results = gene.transcript_set.all()

    for result in results:
        result.five_prime_UTR_locations = json.loads(result.five_prime_UTR_locations)
        result.five_prime_UTR_seqs = json.loads(result.five_prime_UTR_seqs)

        result.cds_locations = json.loads(result.cds_locations)
        result.cds_seqs = json.loads(result.cds_seqs)

        result.intron_locations = json.loads(result.intron_locations)
        result.intron_seqs = json.loads(result.intron_seqs)

        result.three_prime_UTR_locations = json.loads(result.three_prime_UTR_locations)
        result.three_prime_UTR_seqs = json.loads(result.three_prime_UTR_seqs)
        
    return render(request, "searchResult.html", {"gene_info": gene,  "results": results,'species_name':species_name})

@cache_control(no_cache=True)
def blast(request):
    with open(Path(settings.BASE_DIR).joinpath('api/blastdb_config.json'),'r') as f:
        blast_config = json.loads(f.read())
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse(blast_config, safe=False) 
    if request.method == "GET":
        return render(request,'blast.html')
    elif request.method == "POST":
        blast_cmd = "~/Program/miniconda3/bin/"+request.POST["blastOptions"]
        blast_input = request.POST["seq_for_blast"]
        species = request.POST["species"]
        description = request.POST["databaseOptions"]
        for i in blast_config:
            if i['species'] == species:
                for j in i['information']:
                    if j['description'] == description:
                        path = j['path']

        blast = Blast()
        result_token = blast.run(blastCmd=blast_cmd,
                                 blastInput=blast_input,
                                 dbPath=path)

        return redirect(reverse("blast_result", args=[result_token]))
    #return render(request, "blast.html", {"all_db_info": all_db_info})

##if no_cache=True, when user refresh the webpage, the server will render again
@cache_control(no_cache=True)
def blast_result(request, token):
    try:
        result = Blast().show_result(token)
    except ValueError:
        result = 'Error: Database error. Did you select wrong database?'
    if not len(result):
        result = 'No hits found.'
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse(result, safe=False)
    return render(request, "blastresult.html")


def geneStructure(request):
    return HttpResponse("This is GeneStructure Page")


def jbrowse_index(request):
    response = render(request,"jbrowse_index.html",{'species_infos':species_infos})
    return response

def jbrowse_species(request,species):
    
    js = jbrowse_javascript(species=species)
    location = request.GET.get('location',None)
    return render(request,'jbrowse/Cuscuta_australis.html',{'js':js,'location':location})

def jbrowse_static_file(request,species,file):
    import os 
    file_path = os.path.join(settings.BASE_DIR,'jbrowse',species,file)

    ## written by chatgpt
    if os.path.exists(file_path):
        if 'Range' in request.headers:
            # 处理范围请求
            response = FileResponse(open(file_path, 'rb'))

            # 设置响应头部
            response['Accept-Ranges'] = 'bytes'
            response['Content-Length'] = os.path.getsize(file_path)

            # 解析范围请求头部
            range_header = request.headers['Range']
            range_start, range_end = range_header.replace('bytes=', '').split('-')

            # 将范围转换为整数
            if range_start:
                range_start = int(range_start)
            else:
                range_start = 0

            if range_end:
                range_end = min(int(range_end), os.path.getsize(file_path) - 1)
            else:
                range_end = os.path.getsize(file_path) - 1
            # range_start = int(range_start) if range_start else 0
            # range_end = int(range_end) if range_end else os.path.getsize(file_path) - 1
            # 检查范围是否有效
            if range_start >= 0 and range_end < os.path.getsize(file_path) and range_start <= range_end:
                response['Content-Range'] = f'bytes {range_start}-{range_end}/{os.path.getsize(file_path)}'
                response.status_code = 206  # Partial Content
                response['Content-Length'] = range_end - range_start + 1
                response['Accept-Ranges'] = 'bytes'

                # 移动文件指针到范围开始位置
                response.file_to_stream.seek(range_start)

                return response

            return HttpResponse('Invalid range', status=416)  # Range Not Satisfiable

        return FileResponse(open(file_path, 'rb'))

    return HttpResponse('File not found', status=404)

def download(request):
    # links = {}
    return render(request,'download.html',{'species_infos':species_infos})