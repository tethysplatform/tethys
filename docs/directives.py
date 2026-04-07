from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.application import Sphinx


class recipe_gallery_placeholder(nodes.General, nodes.Element):
    """Placeholder node replaced after all docs are read."""

    pass


class RecipeGallery(Directive):
    """
    Directive to insert a recipe gallery into the documentation.
    The gallery can be displayed either as a carousel or a multi-row layout.
    Each line of content should specify a target document link, an image path,
    and optionally tags for the recipe.
    """

    has_content = True
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

        node = recipe_gallery_placeholder()
        node["layout"] = layout
        node["content"] = list(self.content)
        node["docname"] = self.state.document.settings.env.docname
        return [node]


def build_gallery(app, doctree, fromdocname):
    env = app.env
    # Go through all recipe gallery placeholder nodes found - these will be replaced with the fully built gallery nodes
    for placeholder in doctree.findall(recipe_gallery_placeholder):
        layout = placeholder["layout"]
        content = placeholder["content"]
        recipe_count = len(content)

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

        # List to hold all the recipe card nodes to be added to the gallery node
        recipe_card_nodes = []

        for line in content:
            parts = line.split()
            if len(parts) < 2:
                raise ValueError(f"Invalid syntax: {line}")

            # Parse the input on the line into its parts
            link, image_path, *tags = parts
            tags_string = " ".join(tag.strip("[],") for tag in tags)

            # Get the title of the target document
            title = (
                env.titles[link].astext()
                if link in env.titles
                else link.split("/")[-1].replace("_", " ")
            )

            # Resolve the link to the target document
            try:
                link = app.builder.get_relative_uri(fromdocname, link)
            except Exception as e:
                print(f"Could not resolve link {link}: {e}")

            # Create a container for the recipe card with the link, image, and title
            card_container = nodes.container(classes=["recipe-card"])

            # Create the link node that wraps the image, title, and tags
            card_node = nodes.raw(
                "", f'<a href="{link}" class="recipe-link">', format="html"
            )

            image_container = nodes.container(classes=["recipe-image-container"])
            image_node = nodes.image(uri=image_path, alt="Image Not Found")
            image_node["candidates"] = {"*": image_path}
            image_container += image_node

            # Close the anchor tag
            card_close_html = f"""
                <strong class="recipe-title">{title}</strong>
                <p class="recipe-tags">{tags_string}</p>
                </a>
            """
            card_close = nodes.raw("", card_close_html, format="html")

            # Finish building the recipe card
            card_container += card_node  # Opening <a>
            card_container += image_container  # Image
            card_container += card_close  # Closing </a>

            recipe_card_nodes.append(card_container)

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

        # Replace the placeholder node in the doctree with the fully built gallery container node
        placeholder.replace_self(gallery_container_node)


def setup(app: Sphinx):
    """Add the recipe-gallery directive to Sphinx"""
    app.add_node(recipe_gallery_placeholder)
    app.add_directive("recipe-gallery", RecipeGallery)
    app.connect("doctree-resolved", build_gallery)
    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": True}
