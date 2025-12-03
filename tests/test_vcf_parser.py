import pytest
import pandas as pd
from pathlib import Path
from src.pipeline.vcf_parser import VCFParser, VariantAnnotator, Variant

@pytest.fixture
def sample_vcf(tmp_path):
    vcf_content = """##fileformat=VCFv4.2
##contig=<ID=chr10>
##INFO=<ID=GENE,Number=1,Type=String>
##INFO=<ID=TRANSCRIPT,Number=1,Type=String>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
chr10	94761930	rs28371706	G	A	.	.	GENE=CYP2C19
"""
    vcf_file = tmp_path / "test.vcf"
    vcf_file.write_text(vcf_content)
    return str(vcf_file)

def test_variant_annotation():
    annotator = VariantAnnotator()
    variant = annotator.annotate_variant(
        chrom="chr10",
        pos=94761930,
        ref="G",
        alt="A",
        gene="CYP2C19"
    )
    
    assert variant.gene == "CYP2C19"
    assert variant.is_drug_metabolizer_gene is True
    assert variant.cyp_family == "CYP2C19"
    assert variant.clinvar_significance == "pathogenic"

def test_vcf_parsing(sample_vcf):
    parser = VCFParser()
    variants = parser.parse_vcf(sample_vcf)
    
    assert len(variants) == 1
    v = variants[0]
    assert v.chrom == "chr10"
    assert v.pos == 94761930
    assert v.ref == "G"
    assert v.alt == "A"
    assert v.gene == "CYP2C19"

def test_dataframe_conversion(sample_vcf):
    parser = VCFParser()
    variants = parser.parse_vcf(sample_vcf)
    df = parser.variants_to_dataframe(variants)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]['gene'] == "CYP2C19"
