# -*- coding: utf-8 -*-

# Imports
import re
import requests
import pandas as pd
from pyquery import PyQuery

class PDFExtractor(object):
    '''Base class for extracting information from
    PDFs using PDFx.

    '''
    
    def _pdfx(self, pdfname):
        '''Get XML representation of PDF. For details, see 
        http://pdfx.cs.man.ac.uk/usage

        Args:
            pdfname (str) : path to PDF
        Returns:
            XML from PDFX

        '''
        
        # Open PDF
        with open(pdfname, 'rb') as pdf:

            # Send request to PDFX
            req = requests.post(
                'http://pdfx.cs.man.ac.uk', 
                headers={'content-type':'application/pdf'}, 
                data=pdf
            )

            # Return response text
            return req.text

    def _parse_xml(self, xml):
        '''Parse XML using PyQuery.

        Args:
            xml (str) : Raw XML text
        Returns:
            PyQuery object

        '''

        # Remove encoding
        # Note: PyQuery / LXMl will fail if 
        # encodings present
        xml = re.sub('encoding=\'.*?\'', '', xml)

        # Return parsed XML
        return PyQuery(xml)

class MRITableExtractor(PDFExtractor):
    '''Class for extracting tables from PDFs.

    Example:
    > extractor = MRITableExtractor()
    > tables = extractor.pdf_to_mri_tables('article.pdf')

    '''

    # Translation table
    _trans = [
        [u'[\x80-\xff]+', '-'],
    ]
    
    @staticmethod
    def _get_text():
        return PyQuery(this).text()

    def _get_tables(self, xml):
        '''Extract tables from XML string.

        Args:
            xml (str) : XML string from PDFX
        Returns:
            list of tables (pandas.DataFrame-s

        '''
        
        # Parse XML
        qxml = self._parse_xml(xml)
        
        # Get tables
        tables = qxml('table')

        # Initialize tables
        parsed_tables = []
        
        # Loop over tables
        for table in tables:
            
            # Initialize table
            parsed_rows = []
            
            # Get header
            qtable = PyQuery(table)
            headers = qtable.find('th').map(self._get_text)[:]
            
            # Skip if not headers
            if not headers:
                continue
            
            # Get rows
            rows = qtable.find('tr')

            # Loop over rows
            for row in rows:
                
                # Get columns
                qrow = PyQuery(row)
                cols = qrow.find('td').map(self._get_text)[:]

                # Parse column values
                for colidx in range(len(cols)):
                    col = reduce(lambda x, y: re.sub(y[0], y[1], x), self._trans, cols[colidx])
                    try:
                        col = float(col)
                    except ValueError:
                        pass
                    cols[colidx] = col

                # Append parsed columns
                if cols:
                    parsed_rows.append(cols)
            
            # Create data frame
            df = pd.DataFrame(parsed_rows, columns=headers)
            
            # Append parsed table
            parsed_tables.append(df)
        
        # Return parsed tables
        return parsed_tables

    # Header patterns indicating fMRI activation table
    _mri_header_patterns = [
        '^x$', '^y$', '^z$',
        '^ba$', '^lobe$', '^region$',
    ]

    def _is_mri_table(self, table):
        '''Check whether a given table is an fMRI activation table.

        Args:
            table (DataFrame) : table
        Returns:
            True | False

        '''
        
        # Loop over table columns
        for column in table.columns:
            # Loop over regex patterns
            for pattern in self._mri_header_patterns:
                if re.search(pattern, column, re.I):
                    return True
        return False

    def pdf_to_mri_tables(self, pdfname):
        '''Read a PDF document, get XML from PDFX, and extract
        fMRI activation tables.

        Args:
            pdfname (str) : path to PDF
        Returns:
            list of activation tables (pandas.DataFrame-s)
        '''
        
        xml = self._pdfx(pdfname)
        tables = self._get_tables(xml)
        return [table for table in tables if self._is_mri_table(table)]
