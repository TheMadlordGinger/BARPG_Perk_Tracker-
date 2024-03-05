class PerkFilter():
    def filter_perk_list(self, perks):
         results = [];
         for p in perks:
            if self.matches(p):
                results.append(p)
         return results

class TierFilter(PerkFilter):
    def __init__(self):
        self.comparitor ='lt' # lt, le, eq, ge, gt, ne
        self.tier = -1
        
    def matches(self, perk):
        return True;

class TagFilter(PerkFilter):
    def __init__(self, tag):
        self.tag = tag

    def matches(self, perk):
        return self.tag in perk.tags
        
class DescFilter(PerkFilter):
    def __init__(self):
        self.string = ""
        self.mode = "Contains"#Contains,Start with, Ends With
        self.regex = false
        self.inverted = False    
        
class InvertedFilter(PerkFilter):
    def __init__(self, sub_filter):
        self.sub_filter = sub_filter
     
    def matches(self, perk):
        return not self.sub_filter.matches(perk)
        
class CompositeFilter(PerkFilter):
    def __init__(self):
        self.sub_filters = []
    def matches(self, perk):
        for filter in self.sub_filters:
            if not filter.matches(perk):
                return False
        return True
        
       
