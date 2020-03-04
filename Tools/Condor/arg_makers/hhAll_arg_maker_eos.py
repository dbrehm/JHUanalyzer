import subprocess, sys, glob, os
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-t', '--taggers', metavar='FILE', type='string', action='store',
                default   =   'btagHbb,deepTagMD_HbbvsQCD,deepTagMD_ZHbbvsQCD,btagDDBvL',
                dest      =   'taggers',
                help      =   'Taggers to consider (comma separated list) as named in the NanoAOD. Default is btagHbb,deepTagMD_HbbvsQCD,deepTagMD_ZHbbvsQCD,btagDDBvL.')
parser.add_option('-y', '--years', metavar='FILE', type='string', action='store',
                default   =   '16,17,18',
                dest      =   'years',
                help      =   'Years to consider (comma separated list). Default is 16,17,18.')
parser.add_option('-i', '--ignoreset', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'ignoreset',
                help      =   'Setnames from *_loc.txt files to IGNORE (comma separated list). Default is empty.')
parser.add_option('-n', '--name', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'name',
                help      =   'A custom name for this argument list (hh_presel_<name>_args.txt)')

(options, args) = parser.parse_args()

# Options to customize run
years = options.years.split(',')
taggers = options.taggers.split(',')
ignore = options.ignoreset.split(',')
name_string = '_'+options.name if options.name != '' else ''

# Initialize output file
outfile = open('../args/hhAll'+name_string+'_args.txt','w')

base_string = '-i TEMPFILE -o TEMPNAME -c TEMPCONFIG -y TEMPYEAR -d TEMPTAGGER'

for year in years:
    for tagger in taggers:
	for f in [line.rstrip('\n') for line in open('../../../NanoAOD_lists_private/'+year+'.txt')]:
    	    setname = f.split('/')[-1].split('.')[0].split('_')[0]
	    if setname not in ignore:
                outname='HHpreselection'+year+'_'+setname+'_'+tagger+'.root'
                job_string=base_string.replace("TEMPYEAR",year).replace('TEMPTAGGER',tagger).replace('TEMPNAME',outname).replace('TEMPFILE','root://cmsxrootd.fnal.gov//store/user/dbrehm/data18andTTbarSignalMC/rootfiles/'+setname+'_hh'+year+'.root').replace('TEMPCONFIG','hh'+year+'_config.json')
		outfile.write(job_string+'\n')
		if 'data' not in setname and 'QCD' not in setname:
                    for j in [' -J', ' -R', ' -a', ' -b']:
                        for v in [' up',' down']:
			    if j == ' -J': jecname='HHpreselection'+year+'_'+setname+'_JES_'+v.strip()+'_'+tagger+'.root'
			    if j == ' -R': jecname='HHpreselection'+year+'_'+setname+'_JER_'+v.strip()+'_'+tagger+'.root'
			    if j == ' -a': jecname='HHpreselection'+year+'_'+setname+'_JMS_'+v.strip()+'_'+tagger+'.root'
                            if j == ' -b': jecname='HHpreselection'+year+'_'+setname+'_JMR_'+v.strip()+'_'+tagger+'.root'
                            jec_job_string = job_string.replace(outname,jecname) + j + v
                            outfile.write(jec_job_string+'\n')

outfile.close()
