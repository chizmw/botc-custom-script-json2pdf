import sys
from pypdf import PdfReader, PdfWriter

def optimise_pdf(input_file, output_file):
    reader = PdfReader(input_file)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    for page in writer.pages:
        # ⚠️ This has to be done on the writer, not the reader!
        page.compress_content_streams()  # This is CPU intensive!

    writer.add_metadata(reader.metadata)

    with open(output_file, "wb") as fp:
        writer.write(fp)
        
if __name__ == "__main__":
    # input = filename passed in from command line, might include path
    input = sys.argv[1]
    # output is the input filename with .pdf extension replaced with .opt.pdf
    output = input.rsplit(".", maxsplit=1)[0] + ".opt.pdf"
    
    optimise_pdf(input, output)
