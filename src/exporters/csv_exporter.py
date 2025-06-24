"""CSV exporter for analysis results."""

import csv
from typing import List, Dict, Any
from pathlib import Path
import logging

from .base_exporter import BaseExporter
from ..core.models import AnalysisResult
from ..core.exceptions import ExportError

logger = logging.getLogger(__name__)


class CSVExporter(BaseExporter):
    """Export analysis results to CSV format."""
    
    def export(self, results: List[AnalysisResult], filename: str, **kwargs) -> str:
        """Export analysis results to CSV file.
        
        Args:
            results: List of analysis results to export
            filename: Name of the output file (without extension)
            **kwargs: Additional export options
                include_summary: Whether to include summary statistics (default: True)
                
        Returns:
            Path to the exported CSV file
            
        Raises:
            ExportError: If export fails
        """
        include_summary = kwargs.get('include_summary', True)
        output_file = self.output_dir / f"{filename}.csv"
        
        try:
            # Prepare data for export
            data = self._prepare_data(results)
            
            if not data:
                logger.warning("No data to export")
                raise ExportError("No data to export")
            
            # Write main data
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(data)
            
            # Write summary if requested
            if include_summary:
                summary_file = self.output_dir / f"{filename}_summary.csv"
                self._export_summary(results, summary_file)
            
            logger.info(f"Successfully exported {len(data)} rows to {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            raise ExportError(f"Failed to export to CSV: {e}")
    
    def _export_summary(self, results: List[AnalysisResult], output_file: Path) -> None:
        """Export summary statistics to a separate CSV file.
        
        Args:
            results: List of analysis results
            output_file: Path to the summary CSV file
        """
        try:
            summary_stats = self._get_summary_stats(results)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Metric', 'Value'])
                
                for key, value in summary_stats.items():
                    writer.writerow([key.replace('_', ' ').title(), value])
            
            logger.info(f"Summary statistics exported to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export summary: {e}")
            # Don't raise here, as main export succeeded
