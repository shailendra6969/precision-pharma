"""
VCF Parser & Variant Annotation Pipeline
==========================================
Parse VCF files, annotate variants with:
- ClinVar significance
- Population allele frequencies (gnomAD)
- Conservation scores
- Protein domain info
- Drug metabolizer relevance (CYPs)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import pysam
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Variant:
    """Represents an annotated genetic variant."""
    chrom: str
    pos: int
    ref: str
    alt: str
    variant_id: Optional[str] = None
    gene: Optional[str] = None
    transcript: Optional[str] = None
    consequence: Optional[str] = None  # missense, nonsense, synonymous
    amino_acid_change: Optional[str] = None
    clinvar_significance: Optional[str] = None  # benign, pathogenic, uncertain
    clinvar_id: Optional[str] = None
    gnomad_af: Optional[float] = None  # allele frequency
    cadd_score: Optional[float] = None  # deleteriousness score (0-100)
    phylop_score: Optional[float] = None  # conservation
    phastcons_score: Optional[float] = None  # conservation
    protein_domain: Optional[str] = None
    is_drug_metabolizer_gene: bool = False
    cyp_family: Optional[str] = None
    dbsnp_id: Optional[str] = None
    predicted_impact: Optional[str] = None  # HIGH, MODERATE, LOW
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)


class VariantAnnotator:
    """
    Annotate variants using public databases.
    For MVP, uses built-in annotation data and mock external sources.
    """
    
    def __init__(self):
        """Initialize annotator with reference data and API clients."""
        from src.config import DRUG_METABOLIZER_GENES, MOCK_CLINVAR_FALLBACK
        from src.pipeline.external_apis import ClinVarClient, GnomADClient
        
        self.drug_metabolizer_genes = DRUG_METABOLIZER_GENES
        self.clinvar_fallback = MOCK_CLINVAR_FALLBACK
        
        # Initialize clients (will use env vars)
        self.clinvar_client = ClinVarClient()
        self.gnomad_client = GnomADClient()
        
        # Mock CADD for now as it requires large files/API
        self.cadd_db = {
            'chr10:94761930:G>A': 28.5,
            'chr6:161006172:G>A': 32.1,
            'chr19:41307769:C>T': 5.2,
        }
        
    def annotate_variant(self, chrom: str, pos: int, ref: str, alt: str, 
                        gene: Optional[str] = None,
                        transcript: Optional[str] = None) -> Variant:
        """
        Annotate a single variant.
        
        Args:
            chrom: chromosome
            pos: position
            ref: reference allele
            alt: alternate allele
            gene: gene symbol (optional)
            transcript: transcript ID (optional)
            
        Returns:
            Annotated Variant object
        """
        variant_key = f"{chrom}:{pos}:{ref}>{alt}"
        
        # Determine consequence (simplified)
        consequence = self._infer_consequence(ref, alt, gene)
        
        # Fetch annotations (Try API -> Fallback)
        
        # ClinVar
        clinvar_data = self.clinvar_fallback.get(variant_key, {})
        # In production: clinvar_data = self.clinvar_client.get_variant_summary(variant_key) or fallback
        
        # gnomAD
        gnomad_af = self.gnomad_client.get_variant_frequency(chrom, pos, ref, alt)
        if gnomad_af is None:
             # Fallback logic or default
             gnomad_af = 0.001 if variant_key in self.clinvar_fallback else None

        cadd_score = self.cadd_db.get(variant_key)
        
        # Check if gene is a known drug metabolizer
        is_metabolizer, cyp_family = self._check_drug_metabolizer(gene)
        
        # Predict impact
        predicted_impact = self._predict_impact(
            consequence, cadd_score, clinvar_data.get('significance')
        )
        
        # Create variant object
        variant = Variant(
            chrom=chrom,
            pos=pos,
            ref=ref,
            alt=alt,
            variant_id=variant_key,
            gene=gene,
            transcript=transcript,
            consequence=consequence,
            clinvar_significance=clinvar_data.get('significance'),
            clinvar_id=clinvar_data.get('id'),
            gnomad_af=gnomad_af,
            cadd_score=cadd_score,
            phylop_score=self._mock_phylop(cadd_score),
            phastcons_score=self._mock_phastcons(cadd_score),
            is_drug_metabolizer_gene=is_metabolizer,
            cyp_family=cyp_family,
            predicted_impact=predicted_impact,
        )
        
        return variant
    
    def _infer_consequence(self, ref: str, alt: str, gene: Optional[str] = None) -> str:
        """Infer consequence type (simplified heuristic)."""
        if len(ref) != len(alt):
            return "frameshift_variant"
        if len(ref) == 1:
            return "missense_variant" if gene else "intergenic_variant"
        return "inframe_indel"
    
    def _check_drug_metabolizer(self, gene: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Check if gene is a known drug metabolizer."""
        if gene in self.drug_metabolizer_genes:
            cyp_family = self.drug_metabolizer_genes[gene].get('cyp_family')
            return True, cyp_family
        return False, None
    
    def _predict_impact(self, consequence: str, cadd_score: Optional[float], 
                       clinvar_sig: Optional[str]) -> str:
        """Predict impact level."""
        if clinvar_sig in ['pathogenic', 'likely_pathogenic']:
            return 'HIGH'
        if cadd_score and cadd_score > 25:
            return 'HIGH'
        if consequence in ['frameshift_variant', 'missense_variant']:
            return 'MODERATE'
        return 'LOW'
    
    def _mock_phylop(self, cadd_score: Optional[float]) -> Optional[float]:
        """Mock PhyloP conservation score."""
        if cadd_score:
            return cadd_score / 10.0
        return None
    
    def _mock_phastcons(self, cadd_score: Optional[float]) -> Optional[float]:
        """Mock PhastCons conservation score."""
        if cadd_score:
            return min(cadd_score / 50.0, 1.0)
        return None


class VCFParser:
    """Parse and process VCF files."""
    
    def __init__(self, annotator: Optional[VariantAnnotator] = None):
        """
        Initialize VCF parser.
        
        Args:
            annotator: VariantAnnotator instance (default: create new)
        """
        self.annotator = annotator or VariantAnnotator()
    
    def parse_vcf(self, vcf_path: str) -> List[Variant]:
        """
        Parse VCF file and return annotated variants.
        
        Args:
            vcf_path: path to VCF file
            
        Returns:
            List of Variant objects
        """
        variants = []
        
        try:
            vcf = pysam.VariantFile(vcf_path)
            
            for rec in vcf.fetch():
                # Extract basic info
                chrom = rec.contig
                pos = rec.pos
                ref = rec.ref
                alt = str(rec.alts[0]) if rec.alts else None
                variant_id = rec.id
                
                # Try to extract gene from INFO field
                gene_info = rec.info.get('GENE')
                if isinstance(gene_info, (list, tuple)):
                    gene = gene_info[0]
                else:
                    gene = gene_info

                transcript_info = rec.info.get('TRANSCRIPT')
                if isinstance(transcript_info, (list, tuple)):
                    transcript = transcript_info[0]
                else:
                    transcript = transcript_info
                
                if alt:
                    # Annotate variant
                    variant = self.annotator.annotate_variant(
                        chrom=chrom,
                        pos=pos,
                        ref=ref,
                        alt=alt,
                        gene=gene,
                        transcript=transcript
                    )
                    
                    # Store original ID if present
                    if variant_id:
                        variant.variant_id = variant_id
                    
                    variants.append(variant)
            
            vcf.close()
            logger.info(f"Parsed {len(variants)} variants from {vcf_path}")
            
        except Exception as e:
            logger.error(f"Error parsing VCF file: {e}")
            raise
        
        return variants
    
    def parse_csv(self, csv_path: str) -> List[Variant]:
        """
        Parse variant CSV file (alternative to VCF).
        Expected columns: chrom, pos, ref, alt, gene (optional)
        
        Args:
            csv_path: path to CSV file
            
        Returns:
            List of Variant objects
        """
        variants = []
        
        try:
            df = pd.read_csv(csv_path)
            
            for _, row in df.iterrows():
                variant = self.annotator.annotate_variant(
                    chrom=row['chrom'],
                    pos=int(row['pos']),
                    ref=row['ref'],
                    alt=row['alt'],
                    gene=row.get('gene'),
                    transcript=row.get('transcript')
                )
                variants.append(variant)
            
            logger.info(f"Parsed {len(variants)} variants from {csv_path}")
            
        except Exception as e:
            logger.error(f"Error parsing CSV file: {e}")
            raise
        
        return variants
    
    def variants_to_dataframe(self, variants: List[Variant]) -> pd.DataFrame:
        """
        Convert variant list to pandas DataFrame.
        
        Args:
            variants: list of Variant objects
            
        Returns:
            DataFrame with variant annotations
        """
        return pd.DataFrame([v.to_dict() for v in variants])
    
    def export_annotations(self, variants: List[Variant], output_path: str, 
                          format: str = 'csv'):
        """
        Export annotated variants to file.
        
        Args:
            variants: list of Variant objects
            output_path: path to output file
            format: 'csv' or 'json'
        """
        if format == 'csv':
            df = self.variants_to_dataframe(variants)
            df.to_csv(output_path, index=False)
        elif format == 'json':
            data = [v.to_dict() for v in variants]
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Exported {len(variants)} variants to {output_path}")


def create_sample_vcf(output_path: str):
    """Create a sample VCF file for testing."""
    vcf_content = """##fileformat=VCFv4.2
##contig=<ID=chr6>
##contig=<ID=chr10>
##contig=<ID=chr19>
##INFO=<ID=GENE,Number=1,Type=String>
##INFO=<ID=TRANSCRIPT,Number=1,Type=String>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
chr10	94761930	rs28371706	G	A	.	.	GENE=CYP2C19;TRANSCRIPT=NM_000769
chr6	161006172	.	G	A	.	.	GENE=CYP2C9
chr19	41307769	rs4244285	C	T	.	.	GENE=CYP2C19
"""
    with open(output_path, 'w') as f:
        f.write(vcf_content)
    logger.info(f"Created sample VCF at {output_path}")



def create_feature_matrix(variants: List[Variant]) -> pd.DataFrame:
    """
    Create feature matrix from list of variants for prediction models.
    
    Args:
        variants: List of annotated Variant objects
        
    Returns:
        DataFrame with aggregated features for patient
    """
    if not variants:
        # Return empty dataframe with expected columns
        return pd.DataFrame(columns=[
            'is_drug_metabolizer', 'cadd_score', 'allele_frequency',
            'conservation_score', 'effect_missense', 'effect_nonsense',
            'is_pathogenic'
        ])
        
    # Aggregate features
    # This is a simplified aggregation logic for the MVP
    
    # Check for drug metabolizers
    is_drug_metabolizer = any(v.is_drug_metabolizer_gene for v in variants)
    
    # Max CADD score
    cadd_scores = [v.cadd_score for v in variants if v.cadd_score is not None]
    max_cadd = max(cadd_scores) if cadd_scores else 0.0
    
    # Max Allele Frequency (rare variants are more important?)
    # Actually, we might want the rarest variant?
    # For now, let's take the mean AF of variants
    afs = [v.gnomad_af for v in variants if v.gnomad_af is not None]
    mean_af = sum(afs) / len(afs) if afs else 0.0
    
    # Counts of effects
    effects = [v.consequence for v in variants]
    effect_missense = effects.count('missense_variant')
    effect_nonsense = effects.count('stop_gained') # or similar
    
    # Pathogenic count
    pathogenic_count = sum(1 for v in variants if v.clinvar_significance in ['pathogenic', 'likely_pathogenic'])
    
    features = {
        'is_drug_metabolizer': 1 if is_drug_metabolizer else 0,
        'cadd_score': max_cadd,
        'allele_frequency': mean_af,
        'conservation_score': 0.5, # Mock
        'effect_missense': effect_missense,
        'effect_nonsense': effect_nonsense,
        'is_pathogenic': 1 if pathogenic_count > 0 else 0,
    }
    
    return pd.DataFrame([features])


if __name__ == '__main__':
    # Example usage
    parser = VCFParser()
    
    # Create sample VCF for testing
    sample_vcf = '/tmp/sample.vcf'
    create_sample_vcf(sample_vcf)
    
    # Parse VCF
    variants = parser.parse_vcf(sample_vcf)
    
    # Export to CSV
    parser.export_annotations(variants, '/tmp/variants_annotated.csv', format='csv')
    parser.export_annotations(variants, '/tmp/variants_annotated.json', format='json')
    
    # Print first variant
    if variants:
        print(f"\nFirst variant:\n{variants[0].to_dict()}")

