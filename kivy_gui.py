import kivy

from kivy.app import App as KivyApp
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout

from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.lang.builder import Builder

from kivy.core.window import Window

import parser
import filtering as filters

class BGLabel(Label):
    def set_bg(self, color):
       self.bg_color = color
       
    def on_size(self, *args):
        if self.canvas and self.canvas.before:
            self.canvas.before.clear()
            with self.canvas.before:
                Color(*self.bg_color)
                Rectangle(pos=self.pos, size=self.size)

class PerkButton(Button):
    def set_perk(self, perk):
        self.perk = perk
        
    def show_perk_pop_up(self, source):
        desc_label = Builder.load_string("""Label:
    size_hint_y: None
    height: self.texture_size[1]
    text_size: self.width, None
    halign: 'left'
    valign: 'top'""")
   
        text="";
        if self.perk.tier != -1:
            text += "Tier " + ("0","I","II","III")[self.perk.tier]+ "\n"
        if self.perk.cost:
            text += "Cost: " + self.perk.cost + "\n"
        if self.perk.rarity:
            text += "Rarity: " + self.perk.rarity + "\n"
        if self.perk.requires:
            text += "Prerequisites: " + ", ".join(self.perk.requires) + "\n"
        if self.perk.attack:
            text += "Attack: " + self.perk.attack + "\n"
        text += "\n" + self.perk.desc;
        desc_label.text = text;
        
        layout = BoxLayout(orientation='vertical')
        slider = ScrollView( size_hint=(1,.9), bar_width= 12)
        slider.add_widget(desc_label)
        layout.add_widget(slider)
        popup = Popup(content = layout, title = self.perk.breif())
        popup.open()
        
        
        
class App(KivyApp):
    button_size = 50
    button_spacing = 5
    
    def get_perk_button_layout(self):
        if not "__perk_layout__" in self.__dict__:
           self.__perk_layout__ = GridLayout(cols= 1, spacing=App.button_spacing, size_hint_y=None)
        return self.__perk_layout__
        
    def show_filter_window(self, ot):
        layout = BoxLayout(orientation='vertical')
        slider = ScrollView( size_hint=(1,.9), bar_width= 12)
        layout.add_widget(slider)
        filter_layout = StackLayout()
       
        tag_label = Label(text = "Tags", height=80, size_hint_y=None)
        filter_layout.add_widget(tag_label)
        tag_filter_layout = GridLayout(cols= 2, spacing=App.button_spacing, size_hint_y=None)
        tag_filter_layout.height = len(parser.all_tags) * 55
        for tag in parser.all_tags:
            tag_filter_layout.add_widget(Label(text = tag, height=App.button_size))
            tag_filter_layout.add_widget(Button(text = "Showing", height=App.button_size))
        filter_layout.add_widget(tag_filter_layout)   
        
        filter_layout.add_widget(Label(text = "Tiers", height=80, size_hint_y=None))
 
        tier_filter_layout = GridLayout(cols= 2, spacing=App.button_spacing, size_hint_y=None)
        tier_filter_layout.height = 5 * 55
        for tier in ("Teir I", "Teir II","Teir III", "Teir 0", "Untiered"):
            tier_filter_layout.add_widget(Label(text = tier, height=App.button_size, halign="right"))
            tier_filter_layout.add_widget(Button(text = "Showing", height=App.button_size))
        filter_layout.add_widget(tier_filter_layout) 
        
        slider.add_widget(filter_layout);
        popup = Popup(content = layout, title = "Filters")
        popup.open()
        
    def get_perk_list(self):
       result = parser.all_perks;
       result = self.filter.filter_perk_list(result)
       return result
        
    def update_perk_buttons(self):
        perks = self.get_perk_list()
        self.get_perk_button_layout().clear_widgets()
        button_list_size = (App.button_size + App.button_spacing) * len(perks)
        for p in perks:
            x = PerkButton(text=p.breif(), size_hint_y=None, height=App.button_size )
            x.set_perk(p)
            x.bind(on_release = x.show_perk_pop_up)
            self.get_perk_button_layout().add_widget(x)
        self.get_perk_button_layout().height = button_list_size;
    
    
    
    def build(self):
        layout = BoxLayout(orientation='vertical')
        header = BGLabel(text='BARPG Perks', size_hint=(1,.1))
        header.set_bg((0, 0 ,1))
        layout.add_widget(header)
        
        self.filter = filters.CompositeFilter()
        init_filter = filters.TagFilter("Secret");
        init_filter = filters.InvertedFilter(init_filter)
        self.filter.sub_filters.append(init_filter)
        
        #filter_layout = BoxLayout(orientation='horizontal' ,size_hint=(1,None), height=40)
        #filter_button = Button(text="Filter")
        #filter_button.bind(on_release = self.show_filter_window)
        #filter_layout.add_widget(filter_button)
        #layout.add_widget(filter_layout)
        
        slider = ScrollView( size_hint=(1,.8), bar_width= 12)
        self.update_perk_buttons();
        
        slider.add_widget(self.get_perk_button_layout())
        layout.add_widget(slider)
        return layout


if __name__ == '__main__':
    App().run()
    Window.close()

