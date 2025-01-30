from docutils import nodes
from docutils.parsers.rst import Directive, directives


class RecipeGallery(Directive):

    option_spec = {
        "layout": directives.unchanged,
    }

    def run(self):
        # Check if the provided layout option is valid. Note: the default layout is multi-row
        layout = self.options.get("layout", "multi-row")
        if layout not in ["carousel", "multi-row"]:
            raise self.error(
                f"Invalid layout option: {layout}. Use 'carousel' or 'multi-row'."
            )
        
        # Create a container node to hold the gallery
        gallery_container_node = nodes.container()
        gallery_container_node["classes"].append("recipe-gallery-container")

        # If the layout is carousel, add the carousel-container class for functionality and styling
        if layout == "carousel":
            gallery_container_node["classes"].append("carousel-container")

        # Add the inner gallery node to the container
        gallery_node = nodes.container()
        gallery_node["classes"].append(f"{layout}")
        gallery_node["classes"].append("recipe-gallery")

        # Get the Sphinx environment and app
        env = self.state.document.settings.env
        app = env.app
        
        recipe_count = len(self.content)

        # List to hold all the recipe card nodes to be added to the gallery node
        recipe_card_nodes = []

        for line in self.content:
            parts = line.split()
            if len(parts) < 2:
                raise self.error(f"Invalid syntax: {line}")

            # Parse the input on the line into its parts
            link, image_path, *tags = parts
            tags_string = " ".join(tag.strip("[],") for tag in tags)

            # Get the title of the target document
            title = self.get_document_title(env, link)

            # Create a new recipe card node
            card_node = nodes.container(classes=["recipe-card"])

            # Resolve the link to the target document
            try:
                link = app.builder.get_relative_uri(env.docname, link)
            except Exception as e:
                print(f"Could not resolve link {link}: {e}")

            # Create an image container to hold the reference node that will contain the image
            image_container = nodes.container(classes=["recipe-image-container"])
            ref_node = nodes.reference(refuri=link)
            image_node = nodes.image(uri=image_path, alt="Image Not Found")

            # Add the image to the reference node and the reference node to the 
            # image container, then add the image container to the recipe card node
            ref_node += image_node
            image_container += ref_node
            card_node += image_container

            # Add the title and tags to the recipe card node
            card_node += nodes.strong(text=title)
            tags_node = nodes.paragraph(text=tags_string)
            tags_node["classes"].append("recipe-tags")
            card_node += tags_node
            recipe_card_nodes.append(card_node)

        # Add all the recipe card nodes to the gallery node
        for node in recipe_card_nodes:
            gallery_node += node
        gallery_container_node += gallery_node

        # If the layout is carousel and there are more than 4 recipes, add carousel buttons for navigation
        if layout == "carousel" and recipe_count > 4:
            left_button_container_node = nodes.container(
                classes=["carousel-button-left-container"]
            )
            left_button_container_node += nodes.raw(
                "",
                '<button class="carousel-button-left"><i class="fas fa-arrow-left fa-lg"></i></button>',
                format="html",
            )
            gallery_container_node += left_button_container_node
            right_button_container_node = nodes.container(
                classes=["carousel-button-right-container"]
            )
            right_button_container_node += nodes.raw(
                "",
                '<button class="carousel-button-right"><i class="fas fa-arrow-right fa-lg"></i></button>',
                format="html",
            )
            gallery_container_node += right_button_container_node
            return [gallery_container_node]

        return [gallery_container_node]

    def get_document_title(self, env, docname):
        """Get the title of a document by its filename

        Args:
            env: The Sphinx environment
            docname: The name of the document

        Returns:
            str: The title of the document or the docname if the title is not found
        """
        if docname not in env.titles:
            return docname
        return env.titles[docname].astext()
