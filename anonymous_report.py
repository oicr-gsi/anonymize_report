# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 13:19:24 2023

@author: rjovelin
"""



# script to anonymize batch release report


import argparse
import os
import sys
from weasyprint import HTML
import uuid
import shutil

    


def convert_html_to_pdf(html_file, outputfile):
    """
    (str) -> None
    
    Generates a PDF file from a string of HTML
   
    Parameters
    ----------
    - html_file (str): Path to the hhtml file 
    - outputfile (str): Name of the output PDF file
    """
    
    infile = open(html_file)
    html = infile.read()
    infile.close()
    
    htmldoc = HTML(string=html, base_url=__file__)
    htmldoc.write_pdf(outputfile, presentational_hints=True)


def get_project_name(html_file):
    '''
    (str) -> str, str

    Returns the project short and full names extracted from the original html

    Parameters
    ----------
    - html_file (str): Path to the html file 
    '''
    
    infile = open(html_file)
    html = infile.read().strip().split('\n')
    infile.close()
    
    start, end = -1, -1
    html = list(map(lambda x: x.strip(), html))
    while '' in html:
        html.remove('')
    start = html.index('<table id="project_table">')
    end = html.index('</table>', start+1)    
    assert start > 0 and end > 0
    
    L = [i for i in html[start:end] if '<td>' in i]   
    
    project = L[0].split()[1]
    project_name = L[1].split()[1]
    
    return project, project_name


def get_user_ticket(html_file):
    '''
    (str) -> (str, str)
    
    Returns the user name and ticket from the html report
    
    Parameters
    ----------
    - html_file (str): Path to the html report
    '''

    infile = open(html_file)
    html = infile.read().strip().split('\n')
    infile.close()
        
    start = -1
    html = list(map(lambda x: x.strip(), html))
    while '' in html:
        html.remove('')
    start = html.index('<th colspan="2">For internal use only</th>')
    assert start > 0
    
    L = [i for i in html[start: ] if '<td>' in i]

    user = L[0].replace('<td>', '').replace('</td>', '').strip()
    ticket = L[1].replace('<td>', '').replace('</td>', '').strip()
    
    return user, ticket


def group_identifiers(html_file):
    '''    
    (str) -> list
    
    Returns a list with entries from the identifiers table
    
    Parameters
    ----------
    - html_file (str): Path to the html file 
    '''
    
    infile = open(html_file)
    html = infile.read().strip().split('\n')
    infile.close()
    
    start, end = -1, -1
    html = list(map(lambda x: x.strip(), html))
    while '' in html:
        html.remove('')
    start = html.index('<h2>2. Sample information for sequenced libraries</h2>')
    end = html.index('<li>Library Id: OICR-generated library identifier</li>', start+1)
    assert start > 0 and end > 0
    
    L = [i for i in html[start: end] if '<td>' in i]

    return L


def get_identifiers(html_file):
    '''
    (list, str) -> list
    
    Returns a list of parallel list of identifiers extracted from the identifier table of the html report
    
    Parameters
    ----------
    - html_file (str): Path to the original html report
    '''

    # extract identifiers from the identifiers table of the html file
    identifiers = group_identifiers(html_file)


    L = [[], [], [], [], []]

    for k in range(len(L)):
        L[k].extend([identifiers[i].replace('<td>', '').replace('</td>', '').strip() for i in range(k, len(identifiers), 8)])
    assert len(L[0]) == len(L[1]) == len(L[2]) == len(L[3]) == len(L[4])

    return L


def get_file_prefixes(html_file):
    '''
    (str, str) -> list
    
    Returns a list of file prefixes extracted from the html file
    
    Parameters
    ----------
    - html_file (str): Path to the html file to edit
    '''

    infile = open(html_file)
    html = infile.read().strip().split('\n')
    infile.close()

    start, end = -1, -1
    html = list(map(lambda x: x.strip(), html))
    while '' in html:
        html.remove('')
    start = html.index('<h2>3. QC metrics</h2>')
    end = html.index('<h2>4. QC plots</h2>', start+1)
    assert start > 0 and end > 0

    L = [i for i in html[start: end] if '<td>' in i]
    
    prefixes = [L[i].replace('<td>', '').replace('</td>', '').strip() for i in range(1, len(L), 4)]
    
    return prefixes
 

def rename_identifiers(L, project, sample):
    '''
    (list, str, str) -> dict
    
    Returns a dictionary with the identifiers, replacement names for project and for
    all identifiers extracted from the identifier table in report
    
    Parameters
    ----------
    - L (list): List of list of identifiers extracted from the identifier table of the report
    - project (str): Name of the project
    - sample (str): Base of the new identifier name
    '''

    D = {}
    
    k = 1
    
    for i in L:
        if i not in D:
            if i == 'NA':
                D[i] = i
            else:
                if project not in i:
                    newname = sample + '_{0}'.format(k)
                else:
                    newname = sample + '_{0}'.format(k) + '_' + '_'.join(i.split('_')[-2:]) if project not in '_'.join(i.split('_')[-2:])  else sample + '_{0}'.format(k)
                D[i] = newname
                k += 1
    return D 
            
            
def generate_replacement_text(html_file):
    '''
    (str, list) -> dict
    
    Returns a dictionary with anonymized and replacement identifiers for each identifier in the report
    
    Parameters
    ----------
    - pdf_text (list) List of text extracted from the report
    '''

    # get the project names
    project, full_name = get_project_name(html_file)
    
    # parse the identifiers from the identifiers table
    library, case, donor, sample, description = get_identifiers(html_file)
    
    # get the jira ticket and the user name
    user, ticket = get_user_ticket(html_file)

    # parse file prefixes from the metrics table(s)
    prefix = get_file_prefixes(html_file)

    # replace donor Ids
    donors = rename_identifiers(donor, project, 'donor')
    # replace case Ids
    cases = rename_identifiers(case, project, 'case')
    # replace samples Ids
    samples = rename_identifiers(sample, project, 'sample')
    
    # replace library Ids
    libraries = {}
    for i in library:
        for j in cases:
            if j in i:
                libraries[i] = i.replace(j, cases[j])
    
    # replace file prefix
    prefixes = {}
    for i in prefix:
        for j in libraries:
            if j in i:
                prefixes[i] = i.replace(j, libraries[j])
    
    descriptions = {}
    k = 1
    # replace description Ids
    for i in description:
        if i not in descriptions and i not in samples:
            descriptions[i] = 'description_{0}'.format(k)
            k += 1
    
    # rename identifiers
    D = {project: 'PROJECT', full_name: 'PROJECT NAME',
         user: 'XXX-XXX', ticket: ticket.split('-')[0] + 'X' * len(ticket.split('-')[0])}
    
    for i in [donors, cases, samples, libraries, descriptions, prefixes]:
        D.update(i)
            
    return D    


def correct_figure_paths(html_file, plots):
    '''
    (str, list) -> None
    
    Correct the paths to the plot files in the html report with the paths in plots
    
    Parameters
    ----------
    - html_file (str): Path to the html report
    - plots (list): List of paths to figure files in the report
    '''

    # get the directory with plots and html report    
    workingdir = os.path.dirname(html_file)
    
    # extract text from html with corrected image paths
    content = ''
    infile = open(html_file)
    for line in infile:
        if '<img' in line and 'src' in line and './static/images/OICR_Logo_RGB_ENGLISH.png' not in line:
            line = line.split()
            oldpath = line[1][line[1].index('"')+1:line[1].index('"', line[1].index('"')+1)]
            newpath = ''
            for image in plots:
                if os.path.basename(image) in oldpath:
                    newpath = os.path.join(workingdir, os.path.basename(image))
                    break
            if newpath:
                line[1] = line[1].replace(oldpath, newpath)
            else:
                sys.exit('Please provide paths to images in the html report')
            
            content += ' '.join(line)
        else:
            content += line
    infile.close()
    
    # rewrite html file with corrections
    newfile = open(html_file, 'w')
    newfile.write(content)
    newfile.close()
    

def correct_html(html_file, replacements, project):
    '''
    (str, dict) -> None
    
    Correct the paths to the plot files in the html report with the paths in plots
    
    Parameters
    ----------
    - html_file (str): Path to the html report to edit
    - replacements (dict): Dictionary with text to replace
    - project (str): Project short name
    '''

    # extract text from html with corrected image paths
    infile = open(html_file)
    content = infile.read()
    infile.close()
    
    # replace text in tables
    for i in replacements:
        content = content.replace('<td> {0} </td>'.format(i), '<td> {0} </td>'.format(replacements[i]))
   
    # replace name of md5sum file
    content = content.replace('{0}.batch.release'.format(project), replacements[project])    
    
    # rewrite html file with corrections
    newfile = open(html_file, 'w')
    newfile.write(content)
    newfile.close()



def create_workingdir(pdf):
    '''
    (str) -> str
    
    Create and return path to working directory in the same directory of pdf file
    
    Parameters
    ----------
    - pdf (str): Path to the output pdf file
    '''
       
    # create temp dir in dirname of output pdf
    newdir = os.path.join(os.path.dirname(args.pdf), str(uuid.uuid4()))
    os.makedirs(newdir, exist_ok=True)
    return newdir


def anonymize_report(args):
    '''
    (str, list, str) -> None
    
    Generates an anonymized PDF report from a html release report
    
    Parameters
    ----------
    - html_file (str): Path to the html report file 
    - plots (list): List of Path to the figure files in the html report
    - pdf (str): Path to the output anonymized pdf report
    '''     

    newdir = create_workingdir(args.pdf)
    print('created directory:', newdir)

    # copy html and plots in temp dir
    files = [args.html] + list(map(lambda x: x.strip(), args.plots))
    assert all(map(lambda x: os.path.isfile(x), files))
    for file in files:
        destination = os.path.join(newdir, os.path.basename(file))
        shutil.copy(file, destination)
    
    print('copied files to directory')
    
    # edit paths to figure files in html document
    html_file = os.path.join(newdir, os.path.basename(args.html)) 
    correct_figure_paths(html_file, args.plots)

    print('corrected image paths')

    # rename identifiers
    replacements = generate_replacement_text(html_file)
    
    print('generated replacement text')
    
    # replace identifiers in html
    project, full_name = get_project_name(html_file)
    correct_html(html_file, replacements, project)
    
    print('corrected html')
           
    # write anonymized html to pdf
    convert_html_to_pdf(html_file, args.pdf)
     
    print('converted html to pdf')
    
if __name__ == '__main__':

    # create top-level parser
    parser = argparse.ArgumentParser(prog = 'anonymous_report.py', description='A tool to anonymize data release reports')
        
    parser.add_argument('--html', dest='html', help='Path to the html report file', required=True)
    parser.add_argument('--plots', dest='plots', nargs= '*', help = 'List of Path to the figure files in the report', required = True)
    parser.add_argument('--pdf', dest='pdf', help='Output anonymized pdf report', required = True)
    parser.set_defaults(func=anonymize_report)
        
    # get arguments from the command line
    args = parser.parse_args()
    # pass the args to the default function
    args.func(args)