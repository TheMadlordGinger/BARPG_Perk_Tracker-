import urllib.request as url
import re
import os

class Link():
    def __init__(self, text, link):
        self.text = text;
        self.dest = link;
        
    def is_perk_collection(self):
        return self.text.find("Perks") >= 0


class Perk():
    def __init__(self): 
        self.tier = -1
        self.desc = ""
        self.name = ""
        self.tags = []
        self.cost = ""
        self.rarity = ""
        self.requires = []
        self.attack = None
        
    def breif(self):
        return self.name + " (" + ", ".join(self.tags) + ")"
        
    def parse(text, tier, tags=[]):
        result = Perk();
        result.tier = tier;
        result.tags = list(tags);
        i = 0
        lines = text.split("\n")
        for line in lines:
            i+=1;
            if not line:
                break
            tokens = line.split(":", 1)
            if(len(tokens) < 2):
                parse_title(result, line)
            else:
              try:
                  tag, value = tokens
                  tag = tag.strip().lower();
                  tag_parser = tag_parser_look_up[tag];
                  tag_parser(result, value)
              except Exception as e:
                  print("failed parsing:",line)
        result.desc = "\n".join(lines[i:])
        return result
        
def parse_title(perk, text):
      i = text.find('(');
      if i >= 0:
          perk.name = text[:i].strip()
          perk.tags.append(text[i+1:-1].strip())
      else:
          perk.name = text
          
def parse_requires(perk, text):
      text = text.strip()[:-1]
      if text != "None":
          perk.requires = text.split(",")
      
def parse_rarity(perk, text):
     perk.rarity = text    
       
def parse_cost(perk, text):
     perk.cost = text
             
def parse_attack(perk, text):
     perk.attack = text.strip()
     
tag_parser_look_up = {
 "prerequisites": parse_requires, 
 "rarity": parse_rarity, 
 "cost": parse_cost, 
 "costs": parse_cost, 
 "attack": parse_attack}
 
def pull(page):
    content = url.urlopen(page).read()
    str_content = str(content)
    return str_content

def get_link_content(link):
    link_file ="./" + link.text.replace(" ","_") + ".txt"
    link_file = link_file.lower()
    if os.path.isfile(link_file):
        return str("".join(*open(link_file,"r")))
    else:
        print("Pulling", link_file, "from", link.dest)
        content = pull(link.dest)
        print(content, file = open(link_file, "w+"))
        return content;
    
    
text_block_regex = '(DOCS_modelChunk = \[{"ty":"is","ibi":[0-9]+,"s":")(.*?)("})'
def sanitize_text(text):
    text = text.replace("\\\\n","\n")
    text = text.replace("\\xe2\\x80\\x99", "'")
    text = text.replace("\\xe2\\x80\\x9c", "\"")
    text = text.replace("\\xe2\\x80\\x9d", "\"")
    text = text.replace("\\xe2\\x80\\x98", "'")
    text = text.replace("\\\\u0027", "'")
    text = text.replace("\\\\\\\\", "\\")
    text = text.replace("\\\\u0010" , '~')
    text = text.replace("\\\\u0012" , '~')
    text = text.replace("\\\\u001c" , '~\n')
    text = text.replace("\\\\u0011" , '\n~~~\n')
    text = text.replace("\\\\t","   ")
    text = text.replace("\\xe2\\x80\\xa6", "…")
    return text

def find_tiers_index(text):
    tiers = [(0,-1)]
    tier_defs = {"I":1, "II": 2, "III": 3, "0": 0}
    for t in tier_defs:
        try:
            search_text= f'\nTier {t} .*? Perks\n';
            pattern = re.compile(search_text)
            tiers.append((re.search(pattern, text).start(), tier_defs[t]))
        except Exception as e:
            print(f"Missed Tier {t}",e)
    tiers.append((len(text),-1))
    return tiers

def parse_perks_in_link(link):
    print("Parsing Perks", link.text)
    results = []
    tag =  link.text.split("Perks")[0].strip()
    content = get_link_content(link)
    text = re.findall(text_block_regex, content)
    text = "\n".join([sanitize_text(t[1]) for t in text])
    perk_re=re.compile("~~~\n((.*\n)*?)~~~")
    perk_texts = re.finditer(perk_re,text)
    tiers = find_tiers_index(text)
    for p in perk_texts:
        t = 0
        try:
            while p.start() > tiers[t+1][0]:
                t += 1
            t = tiers[t][1]
        except Exception as e :
            print(e)
        try:
            perk  = Perk.parse(p[1], t, [tag]);
            results.append(perk)
        except Exception as e :
            print(e)
    return results
   
def parse_table_of_links(link):
    content = get_link_content(link)
    text = re.findall(text_block_regex, content)
 
    text = sanitize_text(text[0][1])
    links = re.findall('"si":[0-9]*,"ei":[0-9]*,"sm":{"lnks_link":{"lnk_type":0,"ulnk_url":".*?"', content)
    a_links = []
    for lnk in links:
        start = int(re.search('si":([0-9]*)', lnk).group(1))
        end = int(re.search('ei":([0-9]*)', lnk).group(1))
        link_text = text[start-1:end]
        link_dest = re.search('"ulnk_url":"(.*?)"', lnk).group(1)
        a_link = Link(link_text, link_dest)
        if a_link.is_perk_collection():
            a_links.append(a_link)
    perks = []
    for a in a_links:
        l_perks = parse_perks_in_link(a)
        perks += l_perks
    return perks
    
def filter_perks(all_perks):
    result = [];
    for p in all_perks:
        if p.desc == "":
            continue
        result.append(p)
    return result
    
def find_all_tags(all_perks):
    tags = []
    for p in all_perks:
        for t in p.tags:
            if not t in tags:
                tags.append(t)
    tags.sort()
    return tags

toc = Link("main", "https://docs.google.com/document/d/1iFkb8gB4nXb0eyp7sOXtdEjaK6TpxNyZBOU4fUl456g")
all_perks = parse_table_of_links(toc)
all_perks = filter_perks(all_perks)
all_tags = find_all_tags(all_perks);

if __name__ == '__main__':
    print(len(all_perks))
    print(all_tags)
