from db_mani_subcmd import add,delete
import argparse
import asyncio
def add_command(args):
    species_name = args.species_name
    gff_file = args.gff_file_path
    fa_file = args.fa_file_path
    if species_name.find('_') == -1:
        print(f"Your species name {species_name} seems not correct")
        print("Are you sure?(y/N)")
        if(input() == 'y'):
            gff_info = add.GFFParser(gff_file).parse()
            gff_info_with_seqs = add.SeqParser(fa_file,gff_info=gff_info).get_sequence_from_GFFInformation()
            asyncio.run(add.main(gff_info_with_seqs=gff_info_with_seqs,species=species_name))
        else:
            print("Thank you for your using")
            return -1
        print("want to run ")
    else:
        gff_info = add.GFFParser(gff_file).parse()
        gff_info_with_seqs = add.SeqParser(fa_file,gff_info=gff_info).get_sequence_from_GFFInformation()
        asyncio.run(add.main(gff_info_with_seqs=gff_info_with_seqs,species=species_name))
def delete_command(args):
     delete.main()
def main():
    parser = argparse.ArgumentParser(description='Django Database Manipulate Tool')
    subparsers = parser.add_subparsers(dest='command')

    # 创建 add 子命令的解析器
    add_parser = subparsers.add_parser('add', help='Write all gene info of a species into django database')
    delete_parser = subparsers.add_parser('delete',help='Delete all gene info of a species from django database')
    # 添加 add 子命令的参数
    add_parser.add_argument('species_name', help='Species name, underline to separate Genus and Species. e.g:Zea_mays')
    add_parser.add_argument('gff_file_path', help='/Path/to/genome.gff')
    add_parser.add_argument('fa_file_path', help='/Path/to/genome.fa')

    args = parser.parse_args()

    if args.command == 'add':
        add_command(args)
    if args.command == "delete":
        delete_command(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()