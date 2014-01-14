"""

"""

import os
import re
import logging
import subprocess

from .utils import pdf_clean

def pdf_ocr(pdfname, outpath=None):
    """Extract text from a PDF document using Tesseract. First split PDF into
    single-page TIFF images, then run Tesseract on each page.

    :param pdfname: Name of PDF document file
    :param outpath: Directory to save results; defaults to directory of PDF
        document

    """
    split_pages = pdf_split(pdfname, outpath)
    
    text = ''

    for page in split_pages:

        # Build paths
        outname = os.path.splitext(page)[0]
        outname_ext = outname + '.txt'

        logging.debug('Running Tesseract on image {}...'.format(page))

        # Run Tesseract
        subprocess.call(
            [
                'tesseract', page, outname
            ],
            stderr=subprocess.PIPE
        )

        # Try to read and delete Tesseract results; may raise IOError if
        # Tesseract has failed
        try:
            text += open(outname_ext).read()
            os.remove(outname_ext)
        except IOError:
            pass

        try:
            os.remove(page)
        except IOError:
            pass

    return pdf_clean(text)

def pdf_split(pdfname, outpath=None):
    """Split PDF into single-page TIFFs using GhostScript.

    :param pdfname: Name of PDF document file
    :param outpath: Directory to save results; defaults to directory of PDF
        document

    """
    head, tail = os.path.split(os.path.abspath(pdfname))
    name, extension = os.path.splitext(tail)

    outpath = outpath or head

    outname = os.path.join(
        outpath, 
        '{}-page-%03d.tif'.format(name)
    )

    output = subprocess.check_output(
        [
            'gs', '-dBATCH', '-dNOPAUSE', '-sDEVICE=tiffg4',
            '-r300', '-sOutputFile={}'.format(outname), pdfname
        ]
    )
    
    page_match = re.search(r'Page\s*(\d+)\s*$', output)
    npages = int(page_match.groups()[0]) if page_match else 0
    
    return [
        os.path.join(
            outpath, 
            '{}-page-{:03d}.tif'.format(
                name,
                idx+1
            )
        )
        for idx in range(npages)
    ]
