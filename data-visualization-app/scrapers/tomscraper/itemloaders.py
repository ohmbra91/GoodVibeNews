from itemloaders.processors import TakeFirst, MapCompose, Join
from scrapy.loader import ItemLoader

class TomArticleLoader(ItemLoader):
        default_output_processor = TakeFirst()
        datePublished_in = MapCompose(str.strip)
        articleSection_in = MapCompose(str.strip)
        author_in = MapCompose(str.strip)
        headline_in = MapCompose(str.strip)
        link_in = MapCompose(str.strip)        
        
        """datePublished_in = MapCompose(lambda x: x) 
        articleSection_in = MapCompose(lambda x: x) 
        author_in = MapCompose(lambda x: x)   #x.split(" ")[-1])
        headline_in = MapCompose(lambda x: x)
        link_in = MapCompose(lambda x: x) """