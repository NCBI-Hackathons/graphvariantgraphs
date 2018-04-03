from __future__ import print_function
from optparse import OptionParser
import subprocess
import tempfile
import os


def main():
    usage = 'usage: %prog [options] <SRA_id or vcf file>'

    parser = OptionParser(usage)
    parser.add_option('-o', dest='out_dir', default='../results/')
    parser.add_option('-i', dest = 'prefix', default=None, type='str', help='Add prefix [Default: %default]')
    parser.add_option('-v', dest = 'vcf', default=False,  action='store_true', help='VCF input file: %default]')
    parser.add_option('-s', dest = 'sra', default=False,  action='store_true', help='SRA_id: %default]')

    ## TODO: add genome version and species


    (options,args) = parser.parse_args()

    if len(args) != 1:
        parser.error('Must provide SRA id with -s or input vcf file using -v option')
    else:
        input_file = args[0] #or sra_file_path
        save_name = os.path.basename(input_file)

    if (not options.sra and not options.vcf):
        parser.error('Must provide input type using -v or -s')


    if not os.path.isdir(options.out_dir):
        os.mkdir(options.out_dir)

    if options.prefix != None:
        save_name = '%s_%s' %(options.prefix, save_name)

    out_dir = options.out_dir.strip('/') + '/' + save_name + '/'
    print (out_dir)
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
        print ('created %s' %out_dir)

    #check log file:
 #   print (save_name)

    naming_dic = set_naming_convention(save_name, out_dir)
    naming_dic['input_file'] = input_file
    print (naming_dic)

    ###

#   runner(input_file, save_name, options)
  #  run_hisat(naming_dic)


    #map(lambda x: print (check_file_existence(out_dir,  file_name=x, create=False)), naming_dic.keys())

    #runner(sra_file, save_name, options)
    # log_file_name = '%s%s.log' %(options.out_dir, save_name)
    #
    # log_file = open(log_file_name, "a+")
    # log_file.write('~~~~~~ started new run for : %s ~~~~~~~~\n' % save_name)
    #
    # # TODO clean after each successful run
    #
    # if options.vcf != None:
    #     # TODO
    #     #process vcf file
    #     pass
    # else:
    #     log_file.write(save_name)
    #     log_file.write("\n")
    #
    #     print (sra_file, save_name)
    #     log_file.write('started running HISAT2 \n')
    #     bam_file = '%s%s.sort.bam' % (options.out_dir, save_name)
    #
    #     #### ~~~~~~~~~~~~~~ run HISAT2 ~~~~~~~~~~~~~~~~~~~
    #     if not os.path.exists(bam_file):
    #         run_hisat(sra_file, save_name, options.out_dir)
    #
    #     if not os.path.exists(bam_file):
    #         log_file.write('HISAT2 run was unsuccessfull\n')
    #         raise NameError('HISAT2 run was  unsuccessfull')
    #     else:
    #         log_file.write('HISAT2 finished succesfuly\n')
    #
    #     ### ~~~~~~~~~~~~~~ mark_duplicates ~~~~~~~~~~~~~~
    #     log_file.write('started running GATK \n')
    #     mark_duplicates(save_name, options.out_dir)
    #     log_file.write('finished running GATK \n')
    #
    #     ## ~~~~~~~~~~~~~~ BaseRecalibrator ~~~~~~~~~~~~~~
    #
    #
    #     ## ~~~~~~~~~~~~~~ PrintReads ~~~~~~~~~~~~~~
    #
    #
    #     ## ~~~~~~~~~~~~~~ HaplotypeCaller ~~~~~~~~~~~~~~
    #

    ###to do: clean after each run

def runner(input_file, save_name, out_dir, options):

    if options.sra:
        input_type = 'sra'
        vcf_run_stat = False
    elif options.vcf:
        input_type = 'vcf'
        vcf_run_stat = True

    naming_dic = set_naming_convention(save_name)
    naming_dic['input_type'] = input_type

    #    print (naming_dic)
    check_file_existence(file_path=naming_dic['log_file'], create=True)

    log_file = open(out_dir + naming_dic['log_file'])
    log_file.write('~~~~~~ started new run for : %s ~~~~~~~~\n' % save_name)


    # TODO clean after each successful run
    if options.vcf != None:
        # TODO
        # process vcf file
        vcf_run_stat = True
        pass
    else:
        ### do steps to create SRA file from SRA id
        log_file.write(save_name)
        log_file.write("\n")

        print(input_file, save_name)
        log_file.write('started running HISAT2 \n')
        bam_file = '%s%s.sort.bam' % (out_dir, save_name)

        #### ~~~~~~~~~~~~~~ run HISAT2 ~~~~~~~~~~~~~~~~~~~
        if not os.path.exists(bam_file):
            run_hisat(naming_dic)

        if not os.path.exists(bam_file):
            log_file.write('HISAT2 run was unsuccessfull\n')
            raise NameError('HISAT2 run was  unsuccessfull')
        else:
            log_file.write('HISAT2 finished succesfuly\n')

        ### ~~~~~~~~~~~~~~ mark_duplicates ~~~~~~~~~~~~~~
        log_file.write('started running GATK mark_duplicates\n')

        mark_duplicates(naming_dic)

        if (check_file_existence(naming_dic['sorted_markd_bam']) and (check_file_existence(naming_dic['sorted_markd_recal_table']))):
            log_file.write('Marking duplicates finished \n')
        else:
            log_file.write('Marking duplicates was unsuccessfull\n')
            raise NameError('Marking duplicates was unsucessful')
        ## ~~~~~~~~~~~~~~ BaseRecalibrator ~~~~~~~~~~~~~~
        base_recalibrator(naming_dic)

        ## ~~~~~~~~~~~~~~ PrintReads ~~~~~~~~~~~~~~
        print_reads(naming_dic)

        ## ~~~~~~~~~~~~~~ HaplotypeCaller ~~~~~~~~~~~~~~
        haplotype_caller(naming_dic)

        ##~~~~~~~~~~~~~~ Bedtools intersect ~~~~~~~~~~~~

    if vcf_run_stat:
        ### steps after having a VCF file
        pass


def check_file_existence(file_path, create=False):
    if os.path.exists(file_path):
        return True
    elif create:
        new_file = open(file_path, "w")
        print ('created a new empty file just for test')
        new_file.close()
        return True
    else:
        return False



def set_naming_convention(save_name, out_dir):
    '''
    :param save_name:
    :return:

    #
    # ${SRR}.sort.bam
    # ${SRR}.sort.markd.bam - -METRICS_FILE ${SRR}.sort.markd.metrics.bam
    # ${SRR}.sort.markd.recal.table
    # ${SRR}.sort.markd.recal.bam
    # ${SRR}.sort.markd.recal.vcf.gz

    '''
    naming_dic = {
        'save_name': save_name,
        'out_dir': out_dir,
        'log_file': '%s%s.log' %(out_dir,save_name),
        'sorted_bam':'%s%s.sort.bam' %(out_dir,save_name),
        'sorted_markd_bam': '%s%s.sort.markd.bam' %(out_dir,save_name),
        'sorted_marked_metrics': '%s%s.sort.markd.metrics.bam' %(out_dir, save_name),
        'sorted_markd_recal_table':  '%s%s.sort.markd.recal.table' %(out_dir,save_name),
        'sorted_markd_recal_bam': '%s%s.sort.markd.recal.bam' %(out_dir,save_name),
        'sorted_markd_recal_vcf': '%s%s.sort.markd.recal.vcf.gz' %(out_dir,save_name)}

    return (naming_dic)



def run_hisat(naming_dic):

        #TMPDIR=$(mktemp -d -p $(pwd))
        #hisat2 -p ${ALIGN_THREADS} -x /opt/grch38/Homo_sapiens_assembly38 --sra-acc ${SRR} --rg-id ${SRR} --rg SM:${SRR} --rg PL:ILLUMINA| samtools sort -@ ${SORT_THREADS} > ${SRR}.sort.bam -T ${TMPDIR}
        #rmdir ${TMPDIR}
        with tempfile.NamedTemporaryFile(dir=naming_dic['out_dir'], prefix=naming_dic['save_name'], suffix='tmp') as t:
            print (tempfile.mkstemp())
            print (tempfile.gettempdir())
            hisat_cmd = 'hisat2 -p ${ALIGN_THREADS} -x /opt/grch38/Homo_sapiens_assembly38 --sra-acc %s --rg-id %s --rg SM:%s --rg PL:ILLUMINA| samtools sort -@ ${SORT_THREADS} > %s -T %s' %(naming_dic['input_file'], naming_dic['input_file'], naming_dic['input_file'], naming_dic['sorted_bam'], t)
            print (hisat_cmd)
     #   subprocess.call(hisat_cmd, shell=True)


def mark_duplicates(naming_dic):
        #/opt/gatk-4.0.3.0/gatk MarkDuplicates --INPUT ${SRR}.sort.bam --OUTPUT ${SRR}.sort.markd.bam --METRICS_FILE ${SRR}.sort.markd.metrics.bam
        cmd = '/opt/gatk-4.0.3.0/gatk MarkDuplicates --INPUT %s --OUTPUT %s --METRICS_FILE %s' %(naming_dic['sorted_bam'], naming_dic['sorted_markd_bam'], naming_dic['sorted_marked_metrics'])
        print (cmd)
     #   subprocess.call(cmd, shell=True)
def base_recalibrator(naming_dic):
    pass
    ## BaseRecalibrator
    #/opt/gatk-4.0.3.0/gatk BaseRecalibrator -R /opt/grch38/Homo_sapiens_assembly38.fasta --known-sites /opt/grch38/dbsnp_138.hg38.vcf.gz --known-sites /opt/grch38/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz -I ${SRR}.sort.markd.bam -O ${SRR}.sort.markd.recal.table
    cmd = '/opt/gatk-4.0.3.0/gatk BaseRecalibrator -R /opt/grch38/Homo_sapiens_assembly38.fasta --known-sites /opt/grch38/dbsnp_138.hg38.vcf.gz --known-sites /opt/grch38/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz -I %s -O %s' %(naming_dic['sorted_marked_bam'], naming_dic['sorted_markd_recal_table'])
    print (cmd)
#    subprocess.call(cmd, shell=True)


def print_reads(naming_dic):
    pass
    #/opt/gatk-4.0.3.0/gatk ApplyBQSR -R /opt/grch38/Homo_sapiens_assembly38.fasta -I ${SRR}.sort.markd.bam --bqsr-recal-file ${SRR}.sort.markd.recal.table -O ${SRR}.sort.markd.recal.bam


def haplotype_caller(naming_dic):
    pass
    #/opt/gatk-4.0.3.0/gatk HaplotypeCaller -R /opt/grch38/Homo_sapiens_assembly38.fasta --dbsnp /opt/grch38/dbsnp_138.hg38.vcf.gz -I ${SRR}.sort.markd.recal.bam -O ${SRR}.sort.markd.recal.vcf.gz


def bedtools_intersect(naming_dic):
    pass
    #'/home/ubuntu/bin/bedtools intersect -a /home/ubuntu/ldetect_GRCh38/EUR_ldetect.bed -b ${SRR}.sort.markd.recal.vcf.gz -c | sort -k1,1V -k2,2n > ${SRR}.count'
    cmd = '/home/ubuntu/bin/bedtools intersect -a /home/ubuntu/ldetect_GRCh38/EUR_ldetect.bed -b ${SRR}.sort.markd.recal.vcf.gz -c | sort -k1,1V -k2,2n > ${SRR}.count'
# __main__
################################################################################
if __name__ == '__main__':
    main()


## for parallel running:
#parallel -j8 'echo {}' ::: $(seq 1 10)


#####


####