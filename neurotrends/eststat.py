# Import modules
import re

# Import project modules
from reutil import *

######################
# Component patterns #
######################

dfptn1 = """
    (?:                             # Open non-capture group
        \(                            # Open parenthesis
            (?P<df1>%s)     # Capture DF1 value
        \)                            # Close parenthesis
    )                                 # Close non-capture group
""" % (floatptn)

dfptn2 = """
    (?:                             # Open non-capture group
        \(                            # Open parenthesis
            (?P<df1>%s)     # Capture DF1 value
            ,%s                     # Delimiters
            (?P<df2>%s)     # Capture DF2 value
        \)                            # Close parenthesis
    )                                 # Close non-capture group
""" % (floatptn, delimptn, floatptn)

statptn = """
    %s                                # (In)equality
    %s                                # Delimiter
    (?P<stat>%s)            # Capture statistic value
    [,;]?%s                     # Delimiters
    p                                 # p
    %s                                # Delimiter
    (?P<eq>%s)                # Capture (in)equality
    %s                                # Delimiter
    (?P<pval>%s)            # Capture p-value
""" % (eqptn, delimptn, floatptn, delimptn, delimptn, eqptn, delimptn, floatptn)

######################
# Statistic patterns #
######################

def buildstatptn(statname, dfptn):
    
    ptn = """
        \W                            # Not preceded by word
        %s                            # Statistic name
        %s?                         # DF value (optional)
        %s                            # Delimiter
        %s                            # Statistic value
    """ % (statname, dfptn, delimptn, statptn)

    return ptn

tptn = buildstatptn('t', dfptn1)
rptn = buildstatptn('r', dfptn1)
fptn = buildstatptn('f', dfptn2)

statflags = re.VERBOSE | re.IGNORECASE

#############
# Functions #
#############

def eststat(txt, ptn):
    
    statiter = re.finditer(ptn, txt, statflags)
    
    if statiter:
        
        # Initialize correlation list
        stats = []

        for statmatch in statiter:

            # Get named groups
            statdict = statmatch.groupdict()

            # Add DF2 placeholder
            if 'df2' not in statdict:
                statdict['df2'] = None

            # Replace unicode (in)equalities
            if statdict['eq'] in [u'\u2264']:
                statdict['eq'] = '<='
            elif statdict['eq'] in [u'\u2265']:
                statdict['eq'] = '>='

            # Convert numbers to str(float)
            for statpart in ['df1', 'df2', 'stat', 'pval']:
                if statdict[statpart]:
                    try:
                        statdict[statpart] = str(float(statdict[statpart]))
                    # Skip if not float
                    except:
                        continue
            
            # Exclusion conditions
            # Skip negative DF1
            if statdict['df1'] and float(statdict['df1']) < 0:
                continue
            # Skip negative DF2
            if statdict['df2'] and float(statdict['df2']) < 0:
                continue
            # Skip p-values outside [0, 1]
            if not statdict['pval'] or not 0 <= float(statdict['pval']) <= 1:
                continue

            # Add context
            con = getcontext(statmatch, txt)

            # Add statistic to list
            stats.append((statdict, con))

        return stats

    # Return blank if no matches
    return [(None, '')]

# Convenience wrappers
esttstat = lambda txt: eststat(txt, tptn)
estrstat = lambda txt: eststat(txt, rptn)
estfstat = lambda txt: eststat(txt, fptn)
