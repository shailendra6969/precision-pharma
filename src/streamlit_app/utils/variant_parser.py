import streamlit as st
import pandas as pd
from src.pipeline.vcf_parser import VCFParser

class VariantParserService:
    """Service for parsing and annotating variants."""
    
    @staticmethod
    @st.cache_data
    def parse_vcf(file_path: str) -> pd.DataFrame:
        """Parse VCF file and return annotated DataFrame."""
        try:
            parser = VCFParser(file_path)
            variants = parser.parse_vcf(file_path)
            return parser.variants_to_dataframe(variants)
        except Exception as e:
            raise RuntimeError(f"VCF Parsing failed: {e}")

    @staticmethod
    def get_summary_stats(df: pd.DataFrame) -> dict:
        """Calculate summary statistics from variant DataFrame."""
        if df.empty:
            return {}
            
        stats = {
            "total_variants": len(df),
            "unique_genes": df['gene'].nunique() if 'gene' in df.columns else 0,
            "pathogenic_count": 0,
            "drug_metabolizers": 0
        }
        
        if 'clinvar_significance' in df.columns:
            stats["pathogenic_count"] = df[
                df['clinvar_significance'].isin(['pathogenic', 'likely_pathogenic'])
            ].shape[0]
            
        if 'is_drug_metabolizer_gene' in df.columns:
             stats["drug_metabolizers"] = df[df['is_drug_metabolizer_gene'] == True].shape[0]
             
        return stats
