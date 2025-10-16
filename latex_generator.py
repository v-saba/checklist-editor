"""
LaTeX generator for checklist PDFs.
"""
import os
import subprocess

def generate_latex(title, subtitle, phases_data):
    """
    Generate LaTeX content for a checklist.
    
    Args:
        title (str): The checklist title
        subtitle (str): The checklist subtitle
        phases_data (list): List of phases, each containing items
        
    Returns:
        str: The complete LaTeX document content
    """
    latex_content = f'''\\documentclass[12pt]{{article}}
\\usepackage[a4paper, margin=1in]{{geometry}}
\\usepackage{{enumitem}}
\\usepackage{{titlesec}}
\\usepackage{{parskip}}
\\usepackage{{fontspec}}

% Set a simple sans-serif font
\\setmainfont{{PT Sans}}

% Configure section formatting
\\titleformat{{\\section}}
  {{\\normalfont\\bfseries\\large}}{{\\thesection}}{{1em}}{{}}

% Configure enumeration formatting
\\setlist[enumerate]{{leftmargin=2em, label=\\arabic*.}}

\\begin{{document}}

\\begin{{center}}
    {{\\LARGE \\textbf{{{title}}}}}\\\\[1ex]
    \\textit{{{subtitle}}}
\\end{{center}}

\\vspace{{1em}}
'''

    for phase in phases_data:
        latex_content += f'\\section*{{{phase["name"]}}}\n'
        # Only create enumerate environment if there are items
        if phase.get("checklist_items", []):
            latex_content += '\\begin{enumerate}\n'
            for item in phase["checklist_items"]:
                latex_content += f'\\item \\textbf{{{item["read"]}}}'
                if item.get("do"):  # Only add dotfill and "do" part if it exists
                    latex_content += f'\\dotfill{{{item["do"]}}}'
                latex_content += '\n'
            latex_content += '\\end{enumerate}\n'
        latex_content += '\n'

    latex_content += '\\end{document}'
    return latex_content

def compile_pdf(latex_content, temp_dir):
    """
    Compile LaTeX content into a PDF file.
    
    Args:
        latex_content (str): The LaTeX document content
        temp_dir (str): Path to temporary directory for compilation
        
    Returns:
        str: Path to the generated PDF file
        
    Raises:
        subprocess.CalledProcessError: If PDF compilation fails
    """
    # Write LaTeX file
    tex_file = os.path.join(temp_dir, 'checklist.tex')
    with open(tex_file, 'w') as f:
        f.write(latex_content)
    
    try:
        # Run xelatex twice to ensure proper formatting
        for _ in range(2):
            subprocess.run(
                ['xelatex', '-interaction=nonstopmode', '-output-directory', temp_dir, tex_file],
                check=True, 
                capture_output=True
            )
        
        pdf_file = os.path.join(temp_dir, 'checklist.pdf')
        if not os.path.exists(pdf_file):
            raise subprocess.CalledProcessError(1, 'xelatex', 'PDF file not generated')
            
        return pdf_file
    except subprocess.CalledProcessError as e:
        print(f"LaTeX compilation error: {e.stdout.decode() if e.stdout else ''}")
        print(f"LaTeX compilation error (stderr): {e.stderr.decode() if e.stderr else ''}")
        raise 
