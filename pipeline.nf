#!/usr/bin/env nextflow


// Parameters
params.outDir               	= "$baseDir"
//params.inDir               	= "$baseDir/input/"

// Parsing parameters
outDir				= "$params.outDir"

// Scripts
pdf_parser			= "$baseDir/scripts/pdf_parser.py"
json_parser			= "$baseDir/scripts/json_to_db.py"
top_hits			= "$baseDir/scripts/top_hits.py"
snpEFF				= "bash ${baseDir}/snpEff/exec/snpeff"
snpSift			= "java -jar ${baseDir}/snpEff/SnpSift.jar"

vcf_input = Channel.fromPath('input/*.vcf')
pdf_input = Channel.fromPath('input/*.pdf')




process readPDF {
	conda "conda-forge::tika"
	
	input:
	file pdf from pdf_input
		
	output:
	file "${outfile}" into parsed_pdf
	
	script:
	println("Parsing for:\t${pdf.baseName}")
	outfile = "${pdf.baseName}.json"
	"""
	python ${pdf_parser} ${pdf} ${outfile}
	"""
	
}

process parseJson{
	conda "anaconda::psycopg2"
	
	input:
	file json from parsed_pdf


	script:
	// python ${json_parser} ${json}
	"""
	"""

}

process snpEff {
	input:
	file vcf from vcf_input
	
	output:
	file "${vcf.baseName}_ann.vcf" into sort_missense
	file "${vcf.baseName}_ann.vcf" into sort_frameshift
	
	script:
	println("Starting SNP analysis for:\t${vcf}")
	script = "bash ${baseDir}/snpEff/exec/snpeff"
	"""
	${snpEFF} GRCh37.75 -no-downstream -no-intergenic -no-intron -no-upstream -no-utr -verbose ${vcf} > "${vcf.baseName}_ann.vcf"
	"""

}

// Sorteert het geannoteerde vcf bestand op missense
process sortMissense {
	input:
	file annotated from sort_missense
	
	output:
	file "${annotated.baseName}_filtered_missense.vcf" into filtered_missense
	
	script:
	"""
	${snpSift} filter "ANN[0].EFFECT has 'missense_variant'" "${annotated}"  > "${annotated.baseName}_filtered_missense.vcf"
	"""

}

// Sorteert het geannoteerde vcf bestand op frameshift
process sortFramshift{
	input:
	file annotated from sort_frameshift
	
	output:
	file "${annotated.baseName}_filtered_frameshift.vcf" into filtered_frameshift
	
	script:
	"""
	${snpSift} filter "ANN[0].EFFECT has 'frameshift_variant'" "${annotated}"  > "${annotated.baseName}_filtered_frameshift.vcf"
	"""
}

// Dit process haalt de top 10 op van de gesoorteerde frameshift en missense op.
process fetchTopTen{
	publishDir "${baseDir}/results"
	conda "mutirri::httplib2 conda-forge::uritools conda-forge::tqdm jmcmurray::json"
	
	
	input:
	file frameshift from filtered_frameshift
	file missense from filtered_missense
	
	output:
	file "${filename}.json" into end
	
	
	script:
	filename = "${frameshift.baseName.replace("_ann_filtered_frameshift","")}"
	"""
	python ${top_hits} ${missense} ${frameshift} ${filename}
	"""
}





