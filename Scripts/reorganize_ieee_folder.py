import os
import shutil
from compile_papers_data import WORKSPACE, papers_data

ieee_dir = os.path.join(WORKSPACE, "IEEE_Research_Papers")
papers_subfolder = os.path.join(ieee_dir, "Papers")
summaries_subfolder = os.path.join(ieee_dir, "Summaries")

os.makedirs(papers_subfolder, exist_ok=True)
os.makedirs(summaries_subfolder, exist_ok=True)

# 1. Move all PDF files into Papers subfolder
for item in os.listdir(ieee_dir):
    item_path = os.path.join(ieee_dir, item)
    if os.path.isfile(item_path) and item.endswith('.pdf'):
        target = os.path.join(papers_subfolder, item)
        shutil.move(item_path, target)
        print(f"Moved PDF: {item} -> Papers/")

# 2. Copy master summary DOCX into Summaries subfolder
master_docx_src = os.path.join(WORKSPACE, "Documentation", "IEEE_Papers_Summary.docx")
if os.path.exists(master_docx_src):
    shutil.copy(master_docx_src, os.path.join(summaries_subfolder, "IEEE_Papers_Summary.docx"))
    print("Copied master summary docx -> Summaries/")

# 3. Create individual paper summary Markdown files in Summaries subfolder
for p in papers_data:
    summary_filename = f"Paper_{p['id']:02d}_Summary.md"
    summary_path = os.path.join(summaries_subfolder, summary_filename)
    
    content = f"""# Summary: Paper {p['id']} - {p['title']}

**Authors:** {p['authors']}  
**Journal:** {p['journal']} ({p['year']})  
**Volume:** {p['volume']} | **Pages:** {p['pages']}  
**DOI:** https://doi.org/{p['doi']}  
**PDF File:** `IEEE_Research_Papers/Papers/{p['filename']}`  

---

### Abstract
{p['abstract']}

### Key Methodology & Architecture
{p['methodology']}

### Datasets & Benchmarks
{p['datasets']}

### Performance Metrics & Experimental Results
- **Reported Results:** {p['metrics']}
- **Graph X-Axis:** {p['graph_x_y'].split(';')[0] if ';' in p['graph_x_y'] else p['graph_x_y']}
- **Graph Y-Axis:** {p['graph_x_y'].split(';')[1] if ';' in p['graph_x_y'] else p['graph_x_y']}

### Comparative Analysis
- **Pros:** {p['pros']}
- **Cons:** {p['cons']}

### IEEE Citation
`{p['authors']}, "{p['title']}," {p['journal']}, vol. {p['volume']}, pp. {p['pages']}, {p['year']}, doi: {p['doi']}.`
"""
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created summary md: {summary_filename} -> Summaries/")

print("Folder reorganization completed successfully!")
