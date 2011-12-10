"""
Add a function called "markdownify"
Input: the contents of a file in mediawiki format
Output: those contents in markdown
"""
import re
def markdownify(file):
    lines = []
    for line in file:
        lines.extend(line.splitlines())
    return parse_lines(lines)
    

def parse_table(tmp_table):
    table_string=""
    rows = tmp_table.split("|-")[1:]
    col_count = 0
    for row in rows:
        row = row.strip("|! ")
        row = row.replace("||","|")
        if len(row.split("!"))>col_count:
            col_count = len(row.split("!"))
        if len(row.split("|"))>col_count:
            col_count = len(row.split("|"))
    table_data = [] 
    for row in rows:
        row = row.strip("|! ")
        row_data = []
        cells = []
        if len(row.split("!"))>1:
            table_data.append (" | ".join(row.split("!")))
            for i in xrange(col_count):
                row_data.append("--")
            table_data.append("-|-".join(row_data))
            cells = row.split("!")
        
        if len(row.split("|"))>1:
            cells = row.split("|")
            table_data.append(" | ".join(cells))
       
    table_string = "\n".join(table_data)
    #print table_string
    return table_string


def parse_lines(lines):
    parsed_text = ""
    flags = {
            'math':False,
            'nowiki':False,
            'pre':False,
            'code':False,
            'span':False
    }
    header_count = 0
    temp_buf = "" # to keep track the current blob of similar text to process
    table = False
    tmp_table = ""
    for line in lines:
        
        if line.strip()[0:2] == "{|":
            tmp_table = ""
            table = True
        
        if line.strip()[0:2] == "|}":
            table = False
            parsed_text+=parse_table(tmp_table)+"\n\n"
        if table:
            tmp_table+=(line)
            continue
        #print temp_buf
        #fuck that shit
        line = line.replace("<br>","")
        
        
        raw_line = ""
        start_index = 0
        #check if it's heading
        head = re.match(r"(=+)([^=]+)(=+)", line)
        if head:
            header_count+=1
            level = len(head.group(1).strip())-1
            content = parse_text(head.group(2))
            parsed_text += "#"*level+" "+content+"\r\n*****\r\n"
            continue
        i = 0
        while i < len(line):
            c = line[i]
            # the beginning or the end of a tag
            if c == '<':
                
                #no flags are set
                #must be the beginning of a tag
                if sum(flags.values())==0:
                    
                    
                    temp_buf = ""
                    
                    #find what tag it is and set the flag, then skip the pointer to the end of the tag
                    #if the tag is not recognized it is treated as normal text
                    cur_index = 0
                    #+1 to skip to <
                    while i+1+cur_index< len(line) and line[i+1+cur_index] != '>':
                        cur_index += 1
                    tag_name = line[i+1:i+1+cur_index].split(" ")[0]
                    
                    #we recognize the tag, the chunk before the tag must be normal text
                    if tag_name.lower() in flags.keys():
                        temp_buf += line[start_index:i]
                        parsed_text+=parse_text(temp_buf)
                        flags[tag_name.lower()] = True
                        i += cur_index + 2 # increment pointer to the end of tag
                        start_index = i # a new string buffer will start at the end of the tag
                        temp_buf = ""
                    
                #must be the end of a tag
                #some flags are set
                else:
                    
                    cur_index = 0
                   
                    while i+1+cur_index< len(line) and line[i+1+cur_index] != '>':
                        cur_index += 1
                        #+2 to skip the </
                    tag_name = line[i+2:i+1+cur_index].split(" ")[0]
                    if tag_name.lower() in flags.keys():
                        temp_buf += line[start_index:i]
                        if flags['nowiki']:
                            parsed_text+=temp_buf
                            flags['nowiki'] = False
                        if flags['math']:                            
                            parsed_text+="$"+temp_buf+"$"
                            flags['math'] = False
                        if flags['code']:
                            parsed_text+="`" + temp_buf + "`"
                            flags['code'] = False
                        temp_buf = ""
                        i += cur_index + 2 
                        start_index = i 
            i+=1
        if sum(flags.values())==0:
            parsed_text+=parse_text(line[start_index:])+"\n\n"
    return parsed_text
        
def parse_text(txt): 
    parsed_text = ""
    if txt == "":
        return ""
    #check if it has tabbing
    tabcount = 0
    if txt[0]==":":
        while len(txt)>0 and txt[0] == ':':
            tabcount +=1
            txt = txt[1:]
        parsed_text += ""*tabcount
        return parsed_text+parse_text(txt)


    #check if it's a list
    list_level = -1
    list_type = "*"
    if txt[0] == '#' or txt[0] == '*':
        while len(txt)>0 and (txt[0] == '#' or txt[0] == '*'):
            #we just need the last level's type
            list_type = ("* " if txt[0] == '*' else "1. ")
            list_level +=1
            txt = txt[1:]
        parsed_text += "    "*list_level+list_type
        return parsed_text+parse_text(txt)
    
    #check if it's a definition
    if txt[0] == ';':
        txt=txt[1:]
        parsed_text = "**"+parse_text(txt)+"**"
        
        
    #finally replace all italics/bold with proper enclosures, and strip all white space
    parsed_text += txt.replace("'''''","***").replace("'''","**").replace("''","*")
    return parsed_text

#print parse_text("## More number signs gives deeper")
print markdownify(open("test.mediawiki"));