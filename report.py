import csv
from string import Template

def main():
    # open the report template (report.html)
    text_file = open("report.html")
    report_template = Template(text_file.read())
    text_file.close()

    # open the row template (row.html)
    text_file = open("row-1.html")
    row_template = Template(text_file.read())
    text_file.close()

    all_rows = ""
    # open the csv filename (output.csv)
    with open('output.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if reader.line_num > 1:
                str = row_template.substitute(year = row[0], id = row[1], age = row[2], red = row[3], green = row[4], blue = row[5])
                all_rows += str + "\n"

    html = report_template.substitute(rows = all_rows)
    # build a new row for each line in the csv
    # insert the rows into the report template
    # write out our report.html
    print(html)

if __name__ == "__main__":
    main()
