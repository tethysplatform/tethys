from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util.nodes import make_refnode
from sphinx import addnodes

class RecipeGallery(Directive):

    option_spec = {
        "layout": directives.unchanged,
    }

    has_content = True
    
    def run(self):
        layout = self.options.get("layout", "multi-row")

        if layout not in ["carousel", "multi-row"]:
            raise self.error(f"Invalid layout option: {layout}. Use 'carousel' or 'multi-row'.")

        gallery_node = nodes.container()
        gallery_node['classes'].append(f'{layout}')
            
        env = self.state.document.settings.env
        builder = env.app.builder

        recipe_count = len(self.content)

        recipe_card_nodes = []

        for line in self.content:
            parts = line.split('"')
            if len(parts) < 3:
                raise self.error(f"Invalid syntax: {line}")
            first_part = parts[0].strip()
            link, image_path = first_part.split(" ")
            title = parts[1].strip()

            entry_node = nodes.container(classes=['recipe-card'])

            tags = parts[2].strip().strip("[]").split(",")
            tags_string = " ".join(tag.strip() for tag in tags)

            if link:
                try:
                    resolved_link = builder.get_relative_uri(env.docname, link)
                except Exception as e:
                    print(f"Could not resolve link {link}: {e}")
                    resolved_link = link 

                image_container = nodes.container(classes=['recipe-image-container'])
                ref_node = nodes.reference(refuri=resolved_link)
                image_node = nodes.image(uri=image_path, alt="Image Not Found")
                
                ref_node += image_node
                image_container += ref_node
                entry_node += image_container

            else:
                entry_node += nodes.image(uri=image_path, alt=title)

            entry_node += nodes.strong(text=title)
            tags_node = nodes.paragraph(text=tags_string)
            tags_node['classes'].append('recipe-tags')
            entry_node += tags_node
            recipe_card_nodes.append(entry_node)

        if layout == "carousel" and recipe_count > 4: 
            left_button_container_node = nodes.container(classes=['carousel-button-left-container'])
            left_button_container_node += nodes.raw('', '<button class="carousel-button-left hidden">←</button>', format='html')
            gallery_node += left_button_container_node
            print("Reached the add nodes area...")
            for node in recipe_card_nodes:
                gallery_node += node
            right_button_container_node = nodes.container(classes=['carousel-button-right-container'])
            right_button_container_node += nodes.raw('', '<button class="carousel-button-right">→</button>', format='html')
            gallery_node += right_button_container_node
        else:
            for node in recipe_card_nodes:
                gallery_node += node
                
        return [gallery_node]
    
    