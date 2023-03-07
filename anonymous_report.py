# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 13:19:24 2023

@author: rjovelin
"""



# script to anonymize batch release report


import argparse
import os
import sys
#from weasyprint import HTML
#from weasyprint import CSS
# try:
#     from PyPDF2 import PdfReader, PdfWriter
# except:
#     from PyPDF2 import PdfFileReader, PdfFileWriter
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



# def create_temp_pdf(html_file):
#     '''
#     (str) -> str
    
#     Return path to temporary PDF converted from the html file without modifications
        
#     Parameters
#     ----------
#     - html_file (str): Path to the ftml file to be modified
#     '''
    
#     tmp_pdf = html_file[:-4] + str(uuid.uuid4()) + '.pdf' 
#     convert_html_to_pdf(html_file, tmp_pdf)
    
#     return tmp_pdf


# def extract_pdf_text(temp_pdf):
#     '''
#     (str) -> list
    
#     Returns a list of lines in the PDF
    
#     Parameters
#     ----------
#     - temp_pdf (str): Path to the unmodified pdf
#     '''
    
#     try:
#         pdf = PdfReader(temp_pdf)
#     except:
#         pdf = PdfFileReader(temp_pdf)
        
#     T = []

#     #for i in range(pages):
#     for page in pdf.pages:
#         try:
#             text = page.extract_text()
#         except:
#             text = page.extractText()
#         T.extend(text.split('\n'))
    
#     while '' in T:
#         T.remove('')
       
#     return T
    
    

# def get_project_name(pdf_text):
#     '''
#     (list) -> str, str

#     Returns the project short and full names extracted from the PDF

#     Parameters
#     ----------
#     - pdf_text (list): List representation of the unmodified PDF 
#     '''
    
    
#     project = pdf_text[3].split()[0]
#     project_name = ' '.join(pdf_text[3].split()[1:-1])
    
#     return project, project_name



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



    

# def group_identifiers(pdf_text):
#     '''    


#     '''
    
#     start = -1
#     end = -1
#     for i in range(len(pdf_text)):
#         if '2. Sample information for sequenced libraries' in pdf_text[i]:
#             start = i
#         elif 'Library Id: OICR-generated' in pdf_text[i]:
#             end = i
#     assert start > 0 and end > 0
#     L = pdf_text[start: end]
        
#     return L


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








# def group_metrics(pdf_text):
#     '''
    
    
    
#     '''
    
    
#     L = pdf_text[pdf_text.index('3. QC metrics'): pdf_text.index('4. QC plots', pdf_text.index('3. QC metrics') + 1)]
    
#     return L
    
    




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

    # libraries = [identifiers[i].replace('<td>', '').replace('</td>', '').strip() for i in range(0, len(identifiers), 8)]
    # cases = [identifiers[i].replace('<td>', '').replace('</td>', '').strip() for i in range(1, len(identifiers), 8)]
    # donors = [identifiers[i].replace('<td>', '').replace('</td>', '').strip() for i in range(2, len(identifiers), 8)]
    
    # samples = [identifiers[i].replace('<td>', '').replace('</td>', '').strip() for i in range(3, len(identifiers), 8)]
    
    # description = [identifiers[i].replace('<td>', '').replace('</td>', '').strip() for i in range(4, len(identifiers), 8)]
    
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
 
   # prefixes = []
    # infile = open(html_file)
    # for line in infile:
    #     if '<td>' in line:
    #         line = line.strip()
    #         line = line.replace('<td>', '').replace('</td>', '').strip().split('_')
    #         if line[0].startswith(project):
    #             barcode = ''.join(line[-1].split('-'))
    #             if all(map(lambda x: x.upper() in 'ATCG', barcode)):
    #                 prefixes.append('_'.join(line))
    # infile.close()
    # return prefixes



# def get_file_prefixes(metrics, project):
#     '''
#     (list, str) -> list
    
#     '''
    
#     for i in metrics:
#         if i.startswith(project):
#             break
#     metrics = metrics[metrics.index(i): metrics.index('Library Id: OICR generated library identiﬁer.')]        
        
    
#     print(metrics)
    
    
#     prefixes = []
#     for i in range(len(metrics)):
#         if not metrics[i].startswith(project):
#             prefixes.append(metrics[i-1] + '_' + metrics[i])
#     if len(prefixes) == 0:
#         prefixes = metrics        
    
#     print('----')
#     print(prefixes)
    
    
    
#     L = []
#     for i in prefixes:
#         if i.startswith(project):
#             if len(i.split()) not in [1,2]:
#                 print(len(i.split()))
#                 print(i.split())
            
#             assert len(i.split()) == 1 or len(i.split()) == 2
#             if len(i.split()) == 2:
#                 prefix = i.split()[1]
#             else:
#                 prefix = project + i.split(project)[-1]
#             L.append(prefix)
    
#     return L

            

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
            
            
# def generate_replacement_text(html_file, pdf_text):
#     '''
#     (str, list) -> dict
    
#     Returns a dictionary with anonymized and replacement identifiers for each identifier in the report
    
#     Parameters
#     ----------
#     - pdf_text (list) List of text extracted from the report
#     '''

#     # get the project names
#     project, full_name = get_project_name(pdf_text)
    
#     # extract identifiers from identifer table
#     library, case, donor, sample, description = get_identifiers(group_identifiers(pdf_text), project)   
    
#     # get the jira ticket and the user name
#     user = ' '.join(pdf_text[-1].rstrip().split()[:-1])
#     ticket = pdf_text[-1].rstrip().split()[-1]

#     # get the file prefixes
#     # prefix = get_file_prefixes(group_metrics(pdf_text), project)
   
#     # file prefixes are inconsistantly formatted in pdf text, with inconsistent truncations,
#     # making them hard to parse.  instead file prefixes are extracted from the html file   
#     prefix = get_file_prefixes(html_file, project)

#     # replace donor Ids
#     donors = rename_identifiers(donor, project, 'donor')
#     # replace case Ids
#     cases = rename_identifiers(case, project, 'case')
#     # replace samples Ids
#     samples = rename_identifiers(sample, project, 'sample')
    
#     # replace library Ids
#     libraries = {}
#     for i in library:
#         for j in cases:
#             if j in i:
#                 libraries[i] = i.replace(j, cases[j])
    
#     # replace file prefix
#     prefixes = {}
#     for i in prefix:
#         for j in libraries:
#             if j in i:
#                 prefixes[i] = i.replace(j, libraries[j])
    
#     descriptions = {}
#     k = 1
#     # replace description Ids
#     for i in description:
#         if i not in descriptions and i not in samples:
#             descriptions[i] = 'description_{0}'.format(k)
#             k += 1
    
#     # rename identifiers
#     D = {project: 'PROJECT', full_name: 'PROJECT NAME',
#          user: 'XXX-XXX', ticket: ticket.split('-')[0] + 'X' * len(ticket.split('-')[0])}
    
#     for i in [donors, cases, samples, libraries, descriptions, prefixes]:
#         D.update(i)
            
#     return D    


    
    
    
    




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

    #user = ' '.join(pdf_text[-1].rstrip().split()[:-1])
    #ticket = pdf_text[-1].rstrip().split()[-1]

    # get the file prefixes
    # prefix = get_file_prefixes(group_metrics(pdf_text), project)
   
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

    print(replacements)


    # extract text from html with corrected image paths
    infile = open(html_file)
    content = infile.read()
    infile.close()
    
    # replace text in tables
    for i in replacements:
        content = content.replace('<td> {0} </td>'.format(i), '<td> {0} </td>'.format(replacements[i]))
   
    # replace name of md5sum file
    content = content.replace('{0}.batch.release'.format(project), replacements[project])    
    
    print(content)
    
    
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

    # convert html file to temporary pdf
    
    #temp_pdf = 'C:/Users/rjovelin/Desktop/H_drive_bkup/GRD-505/TFRIM4_run_level_data_release_report.2023-03-02.pdf'
    #temp_pdf = create_temp_pdf(html_file)

    #print('converted html to pdf')
    
    # extract text from pdf
    #pdf_text = extract_pdf_text(temp_pdf)

    #print('pdf text')
    #print(pdf_text)
    #print('extracted text from pdf')
    
    
    
    # rename identifiers
    #replacements = generate_replacement_text(html_file, pdf_text)
    
    replacements = generate_replacement_text(html_file)
    
    
    
    
    
    print('generated replacement text')
    
    # replace identifiers in html
    #project, full_name = get_project_name(pdf_text)
    project, full_name = get_project_name(html_file)
    correct_html(html_file, replacements, project)
    
    print('corrected html')
           
    # write anonymized html to pdf
    #convert_html_to_pdf(html_file, args.pdf)
     
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