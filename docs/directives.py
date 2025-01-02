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

        print("Testing layout... ", layout)

        if layout not in ["carousel", "multi-row"]:
            raise self.error(f"Invalid layout option: {layout}. Use 'carousel' or 'multi-row'.")

        gallery_node = nodes.container()
        gallery_node['classes'].append(f'{layout}')

        env = self.state.document.settings.env
        builder = env.app.builder

        recipe_count = len(self.content)
        print("Testing recipe count... ", recipe_count)

        for line in self.content:
            parts = line.split('"')
            print("Testing parts... ", parts)
            if len(parts) < 3:
                raise self.error(f"Invalid syntax: {line}")

            first_part = parts[0].strip()
            link, image_path = first_part.split(" ")
            title = parts[1].strip()

            entry_node = nodes.container(classes=['recipe-card'])

            tags = parts[2].strip().strip("[]").split(",")
            tags_string = " ".join(tag.strip() for tag in tags)

            print("Testing tags: ", tags_string)

            print(f"Testing for toctree now... Link: {link}, Title: {title}")

            if link:
                try:
                    resolved_link = builder.get_relative_uri(env.docname, link)
                    print(f"Resolved link: {resolved_link}")
                except Exception as e:
                    print(f"Could not resolve link {link}: {e}")
                    resolved_link = link 

                ref_node = nodes.reference(refuri=resolved_link)
                ref_node += nodes.image(uri=image_path, alt=title)
                entry_node += ref_node

            else:
                entry_node += nodes.image(uri=image_path, alt=title)

            entry_node += nodes.strong(text=title)
            tags_node = nodes.paragraph(text=tags_string)
            tags_node['classes'].append('recipe-tags')
            entry_node += tags_node

            gallery_node += entry_node

        container_node = nodes.container(classes=['recipe-gallery', f'{layout}'])
        if layout == "carousel" and recipe_count > 4: 
            container_node += nodes.raw('', '<button class="carousel-button-left">←</button>', format='html')
            container_node += gallery_node
            container_node += nodes.raw('', '<button class="carousel-button-right">→</button>', format='html')
        else:
            container_node += gallery_node

        return [container_node]
    
    