import kivy

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.lang.builder import Builder

from kivy.core.window import Window

import parser

class BGLabel(Label):
    def set_bg(self, color):
       self.bg_color = color
       
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.bg_color)
            Rectangle(pos=self.pos, size=self.size)

class PerkButton(Button):
    def set_perk(self, perk):
        self.perk = perk
        
    def show_perk_pop_up(self, source):
        desc_label = Builder.load_string("""Label:
    text_size: self.size
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
           
        desc_label.text = text + "\n" + self.perk.desc
        slider = ScrollView()
        slider.add_widget(desc_label);
        popup = Popup(content =slider,  title=self.perk.breif() )
        popup.open()

class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        header = BGLabel(text='BARPG Perks', size_hint=(1,.1))
        header.set_bg((0, 0 ,1))
        layout.add_widget(header)
        slider = ScrollView( size_hint=(1,.9), bar_width= 12)
        button_size = 50
        button_spacing = 5
        button_list_size = (button_size + button_spacing) * len(parser.all_perks)
        layout2 = GridLayout(cols= 1, spacing=button_spacing, size_hint_y=None, height=button_list_size )
        for p in parser.all_perks:
            x = PerkButton(text=p.breif(), size_hint_y=None, height=button_size )
            x.set_perk(p)
            x.bind(on_release = x.show_perk_pop_up)
            layout2.add_widget(x)
        slider.add_widget(layout2)
        layout.add_widget(slider)
        return layout


if __name__ == '__main__':
    MyApp().run()
    Window.close()

