from Bio.Blast import NCBIXML
from Bio.Blast.Record import HSP
import json
class BlastResultParser:
    def __init__(self,path_of_result:str=None):
        self.path_of_result = path_of_result
        
    def __get_total_spaces(self,q_steps,s_steps):
        if not isinstance(q_steps,list) or not isinstance(s_steps,list):
            raise RuntimeError(f'{q_steps} or {s_steps} is not a list')
        maximum = max(max(q_steps),max(s_steps))
        return len(str(maximum)) + len('Query ') + len('')
    def __get_this_spaces(self,step,total_spaces):
        return total_spaces - len(str(step)) - len('Query ') - len('')
    def __get_one_space(self):
        return ' '
    def split_sequence(self,hsp:HSP,line_length=75):
        lines = []
        #对3个序列切片
        match_split = [hsp.match[i:i + line_length] for i in range(0,hsp.align_length,line_length)]
        q_split = [hsp.query[i:i+line_length] for i in range(0,hsp.align_length,line_length)]
        s_split = [hsp.sbjct[i:i+line_length] for i in range(0,hsp.align_length,line_length)]

        #初始化steps数组
        query_steps = [hsp.query_start - 1]
        if hsp.strand == ('Plus', 'Minus'):
            sbjct_steps = [hsp.sbjct_start]
        elif hsp.strand == ('Plus','Plus') or hsp.strand == (None,None):
            sbjct_steps = [hsp.sbjct_start - 1]
        elif hsp.strand == ('Minus','Plus'):
            raise RuntimeError('Exist Minus/Plus?!')

        #处理steps
        for i in range(len(q_split)):
            if hsp.strand == ('Plus','Minus'):
                next_s_step = sbjct_steps[i] - len(s_split[i]) + s_split[i].count('-')
            else:
                next_s_step = sbjct_steps[i] + len(s_split[i]) - s_split[i].count('-')
            next_q_step = query_steps[i] + len(q_split[i]) - q_split[i].count('-')
            query_steps.append(next_q_step)
            sbjct_steps.append(next_s_step)
        #异常处理，steps不比split多1的情况
        assert len(query_steps) - len(q_split) == 1 and len(sbjct_steps) - len(s_split) == 1, "Steps do not match splits"

        total_spaces = self.__get_total_spaces(query_steps,sbjct_steps)
        #添加start和end信息
        for i in range(len(q_split)):
            line_q = f"Query {query_steps[i] + 1}{self.__get_one_space()*self.__get_this_spaces(query_steps[i],total_spaces)} "\
                     + q_split[i] + f' {query_steps[i+1]}'
            line_match = f" {self.__get_one_space()*total_spaces}"+match_split[i]
            if hsp.strand == ('Plus','Minus'):
                line_s = f"Sbjct {sbjct_steps[i]}{self.__get_one_space()*self.__get_this_spaces(sbjct_steps[i],total_spaces)} " + s_split[i] + f" {sbjct_steps[i+1] + 1}\n"
            else:
                line_s = f"Sbjct {sbjct_steps[i] + 1}{self.__get_one_space()*self.__get_this_spaces(sbjct_steps[i],total_spaces)} " + s_split[i] + f' {sbjct_steps[i + 1]}\n'
            lines.append(line_q)
            lines.append(line_match)
            lines.append(line_s)
        return '\n'.join(lines)

    def parse(self):
        self.blast_xml_handle = open(self.path_of_result)
        self.blast_records = NCBIXML.parse(self.blast_xml_handle)
        res = []
        for record in self.blast_records:
            #print(record.__dict__.keys())
            for alignment in record.alignments:
                res_dict = {"hit_id": "", "hsp_info": "", "hit_score":""}
                hit_id = alignment.hit_def
                res_dict["hit_id"] = hit_id
                hsps = []
                for hsp in alignment.hsps:
                    #print(hsp.__dict__)
                    hit_info = f'length={hsp.align_length}'
                    hit_info+=f'\nScore={hsp.bits} bits({hsp.score}),\tExpect={hsp.expect}'
                    hit_info+=f'\nIdentities={hsp.identities}/{hsp.align_length}(%.2f%%)'%(hsp.identities/hsp.align_length*100)
                    hit_info+=f',\tGaps={hsp.gaps}/{hsp.align_length}(%.2f%%)'%(hsp.gaps/hsp.align_length*100)
                    hit_info+=f',\nStrand={hsp.strand[0]}/{hsp.strand[1]}'
                    align_info = self.split_sequence(hsp)
                    hit_info += f'\n\n{align_info}'
                    hsps.append(hit_info)
                res_dict['hsp_info'] = hsps

                try:
                    res_dict['hit_score'] = alignment.hsps[0].expect
                except IndexError:
                    pass

                res.append(res_dict)
        self.blast_xml_handle.close()
        return res

class Blast(BlastResultParser):
    def __init__(self):
        import os
        self.__BLASTCACHE = os.path.join(os.getcwd(), 'blast_cache/')

    def __random_token(self):
        import hashlib
        import os
        return hashlib.sha1(os.urandom(24)).hexdigest()

    def __cmd_run(self, cmd_string, cwd=None, retry_max=5, silence=False, log_file=None):
        import subprocess
        if not silence:
            print("Running " + str(retry_max) + " " + cmd_string)
        p = subprocess.Popen(cmd_string, shell=True,
                             stderr=subprocess.PIPE, stdout=subprocess.PIPE, cwd=cwd)
        output, error = p.communicate()
        if not silence:
            print(error.decode())
        returncode = p.poll()
        # module_logger.info("Finished bash cmd with returncode as %d" % returncode)
        if returncode == 1:
            if retry_max > 1:
                retry_max = retry_max - 1
                self.__cmd_run(cmd_string, cwd=cwd, retry_max=retry_max)

        output = output.decode()
        error = error.decode()

        return (not returncode, output, error)



    def run(self, blastCmd, dbPath, blastInput):
        '''调用shell, 运行blast的cmd'''
        import os
        result_token = self.__random_token()
        query_token = self.__random_token()
        path = self.__BLASTCACHE
        query = path + "query+" + query_token
        output = path + "result+" + result_token
        cmd = "%s -db %s -query %s -out %s -outfmt 5" % (blastCmd, dbPath, query, output)
        with open(query, "w") as f:
            f.write(blastInput)
        try:
            self.__cmd_run(cmd)
        except:
            pass
        finally:
            os.system(f"rm {query}")
        return result_token

    def blast_result_to_json(self, path_of_result_file):
        '''
        输入BLAST+ 2.5.0版本的输出文件,将db_info, blast_summary和所有的mapping信息提取出来, 返回json
        '''
        import re
        import json
        json_dict = {"db_info": "", "summary": "", "mapping_info": {}}
        with open(path_of_result_file, "r") as f:
            info = f.read()
        try:
            info.index("***** No hits found *****")
            json_dict["summary"] = "***** No hits found *****"
            return json.dumps(json_dict)
        except ValueError:
            pass
        data_base_info = re.search(
            pattern="Database.*sequences.*total\sletters", string=info, flags=re.S)[0]
        summary_info = re.search(
            pattern="Query.*>", string=info[:info.index(">")+1], flags=re.S)[0]  # 从Query匹配到第一个>
        mapping_info = re.search(
            pattern=">.*Lam", string=info[:info.index("Posted date")], flags=re.S)[0]  # 从>匹配到第二个Lambda
        # 错误处理
        # if ** is None:
        summary_info = summary_info[:len(summary_info)-1].rstrip()  # 去掉 >
        mapping_info = mapping_info[:len(mapping_info)-3].rstrip()  # 去掉末尾Lam
        try:
            print(mapping_info)
            mapping_info = re.search(
                ">.*Lam", mapping_info,flags=re.S)[0]  # 从>匹配到第一个lambda
            mapping_info = mapping_info[:len(
                mapping_info)-3].rstrip()  # 去掉末尾Lam
        except Exception as e:
            print(e)
        mapping_info_splited = mapping_info.split(">")
        for gene_mapped_info in mapping_info_splited:
            if not gene_mapped_info:
                continue
            id = re.search(pattern="\S*\n", string=gene_mapped_info)[0]
            mapped_info = gene_mapped_info.replace(id, "")
            json_dict["mapping_info"][id] = mapped_info
        json_dict["db_info"] = data_base_info
        json_dict["summary"] = summary_info
        return json.dumps(json_dict)

    def show_result(self, token_of_result_file):
        import re
        import os
        path_of_result_file = os.path.join(
            os.getcwd(), "blast_cache/") + "result+" + token_of_result_file
        
        self.path_of_result = path_of_result_file
        blast_result_json = self.parse()
        #print(blast_result_json)
        return blast_result_json



if __name__ == "__main__":
    path = "/lustre/home/web_base/Work/yuechen/ParasiticPlantsBase/blast_cache/result+6fb5eedff0f71c4bea322fffa4aa7aadaf270ea5"
    path2 = "/lustre/home/web_base/Work/yuechen/ParasiticPlantsBase/blast_cache/result+0c3182a7c7f204e169d2bc7274e156e3f33d042c"
    path3 = "/lustre/home/web_base/Work/yuechen/ParasiticPlantsBase/blast_cache/result+ceda22234b1b86b02ccf4946ca82f957497fa601"
    
    blast = Blast()
    print(blast.show_result("123"))
    #print(blast.blast_result_to_json(path3))
