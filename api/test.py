from blastTools import BlastResultParser

result = BlastResultParser('../blast_cache/result+f5ceaa340daa78c6bc8c57119cba9ce29bf7910e')
result.parse()
# for i in result.parse():
#     print(f'{i["hit_id"]}\t{i["hit_score"]}')
#     for j in i['hsp_info']:
#         print(j)